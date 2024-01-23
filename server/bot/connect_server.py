import requests


class UsersService:
    limit = 5
    # base_url = f"http://{os.environ['WEB_APP_HOST']}:8000/api/"
    base_url = f"http://127.0.0.1:8000/api/"

    def check_connect(self):
        response = requests.get(f"{self.base_url}ping/")
        print('status 200')
        response.raise_for_status()

    def get_chats(self, query_params=False):
        if query_params == False:
            response = requests.get(f"{self.base_url}chats/")
        else:
            response = requests.get(f"{self.base_url}chats/", query_params)
        response.raise_for_status()
        return response.json()

    def patch_chat(self, chat_data, chat_id):
        response = requests.patch(f"{self.base_url}chat/{chat_id}/", json=chat_data)
        response.raise_for_status()
        return response.json()

    def post_chat(self, chat_data):
        response = requests.post(f"{self.base_url}chats/", json=chat_data)
        response.raise_for_status()
        return response.json()


db_service = UsersService()