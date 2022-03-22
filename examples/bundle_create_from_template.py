from blueinkclient import Client



if __name__ == "__main__":
    client = Client()
    bundles = client.bundles.list()
    print(bundles.body)