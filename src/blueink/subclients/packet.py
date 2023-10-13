from blueink import endpoints
from blueink.request_helper import NormalizedResponse
from blueink.subclients.subclient import SubClient


class PacketSubClient(SubClient):
    def update(self, packet_id: str, data: dict) -> NormalizedResponse:
        """Update a Packet

                Note: this always performs a partial update (PATCH) because that is
                the only method supported by the Blueink API for this endpoint

                Args:
                    packet_id: the ID of the Packet
                    data: the updated field values for the Packet
        * Update via ```client.webhooks.update(...)```

                Returns:
                    A NormalizedResponse, with the updated packet as `data`

                Raises:
                     exceptions.RequestException (or a more specific exception class)
                     if an error occured
        """
        url = self.build_url(endpoints.PACKETS.UPDATE, packet_id=packet_id)
        return self._requests.patch(url, json=data)

    def embed_url(self, packet_id: str) -> NormalizedResponse:
        """Create an embedded signing URL

        deliver_via on the Packet must be set to "embed" for this request
        to succeed.

        Args:
            packet_id: the ID of the Packet.

        Returns:
            A NormalizedResponse
        """
        url = self.build_url(endpoints.PACKETS.EMBED_URL, packet_id=packet_id)
        return self._requests.post(url)

    def retrieve_coe(self, packet_id: str) -> NormalizedResponse:
        url = self.build_url(endpoints.PACKETS.RETRIEVE_COE, packet_id=packet_id)
        return self._requests.get(url)

    def remind(self, packet_id: str) -> NormalizedResponse:
        """Send a reminder to this Packet

        Args:
            packet_id: the ID of the Packet

        Returns:
            A NormalizedResponse
        """
        url = self.build_url(endpoints.PACKETS.REMIND, packet_id=packet_id)
        self._requests.put(url)
