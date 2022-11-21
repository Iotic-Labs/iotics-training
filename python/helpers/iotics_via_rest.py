import base64
import json
from datetime import datetime, timedelta, timezone
from typing import Callable, List, Tuple

import stomp
from iotic.web.stomp.client import StompWSConnection12
from requests import request


class IOTICSviaREST:
    def __init__(self, host_url: str, stomp_url: str = None):
        self._headers = None
        self._stomp_client = None
        self._host = host_url
        self._host_id = None
        self._stomp_url = stomp_url

    def setup(self, token: str):
        self._headers = {
            "accept": "application/json",
            "Iotics-ClientAppId": "example_code",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        self._host_id = self.get_host_id()
        if self._stomp_url:
            self._stomp_client = StompClient(
                endpoint=self._stomp_url, callback=self.receiver_callback
            )
            self._stomp_client.setup(token=token)

    def _make_api_call(self, method: str, endpoint: str, payload: dict = None) -> dict:
        try:
            response = request(
                method=method, url=endpoint, headers=self._headers, json=payload
            )
            response.raise_for_status()
        except Exception as ex:
            print("Getting error", ex)

        return response.json()

    def get_host_id(self) -> str:
        host_id = self._make_api_call(
            method="GET", endpoint=f"{self._host}/qapi/host/id"
        )

        return host_id.get("hostId")

    def create_twin(self, twin_did: str):
        self._make_api_call(
            method="POST",
            endpoint=f"{self._host}/qapi/twins",
            payload={"id": twin_did},
        )

        print(f"Twin {twin_did} created")

    def describe_twin(self, twin_did: str) -> str:
        twin_description = self._make_api_call(
            method="GET",
            endpoint=f"{self._host}/qapi/hosts/{self._host_id}/twins/{twin_did}",
        )

        return json.dumps(twin_description, indent=4)

    def delete_twin(self, twin_did: str):
        self._make_api_call(
            method="DELETE",
            endpoint=f"{self._host}/qapi/hosts/{self._host_id}/twins/{twin_did}",
        )

        print(f"Twin {twin_did} deleted")

    def upsert_twin(
        self,
        twin_did: str,
        location: dict = None,
        properties: List[dict] = None,
        feeds: List[dict] = None,
        inputs: List[dict] = None,
    ):
        payload = {"twinId": {"hostId": self._host_id, "id": twin_did}}

        if location:
            payload.update({"location": location})
        if feeds:
            payload.update({"feeds": feeds})
        if inputs:
            payload.update({"inputs": inputs})
        if properties:
            payload.update({"properties": properties})

        self._make_api_call(
            method="PUT", endpoint=f"{self._host}/qapi/twins", payload=payload
        )

        print(f"Twin {twin_did} upserted")

    def search_twins(
        self,
        scope: str = "LOCAL",
        response_type: str = "FULL",
        properties: List[dict] = None,
        text: str = None,
        timeout: int = 5,
    ):
        # Initialise an empty list.
        # It will contain the list of Twins retrieved by the search
        twins_list = []

        # Add a new temporary field in the headers.
        # Client request timeout is used to stop the request processing once the timeout is reached
        headers = self._headers.copy()
        headers.update(
            {
                "Iotics-RequestTimeout": (
                    datetime.now(tz=timezone.utc) + timedelta(seconds=timeout)
                ).isoformat(),
            }
        )

        filters = {}

        if properties:
            filters["properties"] = properties
        if text:
            filters["text"] = text

        with request(
            method="POST",
            url=f"{self._host}/qapi/searches",
            headers=headers,
            stream=True,
            verify=True,
            params={"scope": scope},
            json={
                "responseType": response_type,
                "filter": filters,
            },
        ) as resp:
            # Raises HTTPError, if one occurred
            resp.raise_for_status()
            # Iterates over the response data, one line at a time
            for chunk in resp.iter_lines():
                response = json.loads(chunk)
                twins_found = []
                try:
                    twins_found = response["result"]["payload"]["twins"]
                except KeyError:
                    continue
                finally:
                    if twins_found:
                        # Append the twins found to the list of twins
                        twins_list.extend(twins_found)

        print(f"Found {len(twins_list)} twin(s)")

        return twins_list

    def send_input_message(
        self,
        twin_sender_did: str,
        twin_receiver_did: str,
        twin_receiver_host_id: str,
        input_id: str,
        message: str,
    ):
        encoded_data = base64.b64encode(json.dumps(message).encode()).decode()
        payload = {"message": {"data": encoded_data, "mime": "application/json"}}

        self._make_api_call(
            method="POST",
            endpoint=f"{self._host}/qapi/hosts/{self._host_id}/twins/{twin_sender_did}/interests/hosts/{twin_receiver_host_id}/twins/{twin_receiver_did}/inputs/{input_id}/messages",
            payload=payload,
        )

        print(f"Message {message} sent")

    def wait_for_input_messages(self, twin_receiver_did: str, input_id: str):
        endpoint = (
            f"/qapi/hosts/{self._host_id}/twins/{twin_receiver_did}/inputs/{input_id}"
        )

        print("Waiting for Input messages...")

        self._stomp_client.subscribe(
            destination=endpoint,
            subscription_id=f"{twin_receiver_did}-{input_id}",
            headers=self._headers,
        )

    @staticmethod
    def receiver_callback(headers, body):
        encoded_data = json.loads(body)

        try:
            time = encoded_data["message"]["occurredAt"]
            data = encoded_data["message"]["data"]
        except KeyError:
            print("A KeyError occurred in the receiver_callback")
        else:
            decoded_feed_data = json.loads(base64.b64decode(data).decode("ascii"))
            print(f"Last Input msg received at {time}: {decoded_feed_data}")


class StompClient:
    def __init__(
        self,
        endpoint: str,
        callback: Callable,
        heartbeats: Tuple[int, int] = (10000, 10000),
    ):
        self._endpoint = endpoint
        self._stomp_client = None
        self._heartbeats = heartbeats
        self._callback = callback

    def setup(self, token: str):
        self._stomp_client = StompWSConnection12(
            endpoint=self._endpoint, heartbeats=self._heartbeats
        )
        self._stomp_client.set_ssl(verify=True)
        self._stomp_client.set_listener(
            name="stomp_listener",
            lstnr=StompListener(
                stomp_client=self._stomp_client, callback=self._callback
            ),
        )

        self._stomp_client.connect(wait=True, passcode=token)

    def subscribe(self, destination, subscription_id, headers):
        self._stomp_client.subscribe(
            destination=destination, id=subscription_id, headers=headers
        )

    def disconnect(self):
        self._stomp_client.disconnect()


class StompListener(stomp.ConnectionListener):
    def __init__(self, stomp_client, callback):
        self._stomp_client = stomp_client
        self._callback = callback

    def on_error(self, headers, body):
        print(f"Received an error {body}")

    def on_message(self, headers, body):
        self._callback(headers, body)

    def on_disconnected(self):
        self._stomp_client.disconnect()
        print("Disconnected")
