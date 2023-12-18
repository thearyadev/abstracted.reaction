import qbittorrentapi
from qbittorrentapi import TorrentDictionary
import os


def get_all_completed_pending_torrents() -> list[]:
    client = qbittorrentapi.Client(host="192.168.1.107", port=63861, username="admin", password="adminadmin")
    client.auth_log_in()
    # torrents = [torrent for torrent in client.torrents_info() if torrent.status == "seeding" or torrent.status ==
    # "complete"]i print(torrents)idna
    print(client.torrents_info()[0].files)


def add_new_torrent()


get_all_completed_pending_torrents()
