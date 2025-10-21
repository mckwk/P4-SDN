import json
import requests

class Controller:
    def __init__(self, switch_ip, switch_port):
        self.switch_ip = switch_ip
        self.switch_port = switch_port
        self.base_url = f"http://{self.switch_ip}:{self.switch_port}/"

    def add_flow(self, flow):
        url = self.base_url + "flows"
        response = requests.post(url, json=flow)
        if response.status_code == 201:
            print("Flow added successfully.")
        else:
            print("Failed to add flow:", response.text)

    def delete_flow(self, flow_id):
        url = self.base_url + f"flows/{flow_id}"
        response = requests.delete(url)
        if response.status_code == 204:
            print("Flow deleted successfully.")
        else:
            print("Failed to delete flow:", response.text)

    def get_flows(self):
        url = self.base_url + "flows"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print("Failed to retrieve flows:", response.text)
            return []

    def update_flow(self, flow_id, flow):
        url = self.base_url + f"flows/{flow_id}"
        response = requests.put(url, json=flow)
        if response.status_code == 200:
            print("Flow updated successfully.")
        else:
            print("Failed to update flow:", response.text)

# Example usage
if __name__ == "__main__":
    controller = Controller("127.0.0.1", 8080)
    flow = {
        "id": "flow1",
        "match": {
            "in_port": 1,
            "eth_type": 0x0800
        },
        "actions": [
            {"type": "output", "port": 2}
        ]
    }
    controller.add_flow(flow)