"""main.py: Python class that uses kalturaclient library to perform media upload and search media entries"""

__author__ = "Gowtham Manivelan"
__credits__ = ["Kaltura"]
__version__ = "1.0.0"
__maintainer__ = "Gowtham Manivelan"
__email__ = "gowthammanivelan@gmail.com"
__status__ = "Development"


from KalturaClient import *
from KalturaClient.Plugins.Core import *
import json
from constants import k_type, user_id, secret, partner_id, expiry, privileges, service_url


class KalturaStream:

    def __init__(self, secret, user_id, k_type, partner_id, expiry, privileges, service_url):
        self.secret = secret
        self.k_type = k_type
        self.user_id = user_id
        self.partner_id = partner_id
        self.expiry = expiry
        self.privileges = privileges
        self.session = None
        self.config = KalturaConfiguration()
        self.config.serviceUrl = service_url
        self.client = None
        self.search_tag = None
        self.entry = None
        self.upload_token_id = None
        self.video_exists = False

    def initiate_client(self):
        """
        Initiate kaltura session object using KalturaClient library
        """
        self.client = KalturaClient(self.config)

    def set_session(self):
        """
        create a kaltura session
        """
        self.session = self.client.session.start(self.secret, self.user_id, self.k_type, self.partner_id, self.expiry,
                                                 self.privileges)
        self.client.setKs(self.session)
        print("SESSION ACTIVE")

    def list_entries(self, filter_name):
        """
        list all the media entries matching the filtername
        :param filter_name: str
        :return: entries_list: jsonArray
        """
        try:
            filter_tag = KalturaMediaEntryFilter()
            filter_tag.nameLike = filter_name
            pager = KalturaFilterPager()
            self.search_tag = self.client.media.list(filter_tag, pager)
            entries_list = []
            for entry in self.search_tag.objects:
                obj = json.loads(json.dumps(entry, default=lambda entry: entry.__dict__))
                entries_list.append(obj.copy())
            return json.dumps(entries_list)
        except Exception as e:
            print(e)

    def create_media_entry(self, media_entry_name, media_entry_description):
        """
        create a new media entry
        :param media_entry_name: str
        :param media_entry_description: str
        :return: media_entry_response json
        """
        try:
            media_entry = KalturaMediaEntry()
            media_entry.name = media_entry_name
            media_entry.description = media_entry_description
            media_entry.mediaType = KalturaMediaType.VIDEO
            self.entry = self.client.media.add(media_entry)
            result = self.entry
            print("MEDIA ENTRY CREATED")
            media_entry_response = json.loads(json.dumps(result, default=lambda result: result.__dict__))
            return json.dumps(media_entry_response)
        except Exception as e:
            print(e)

    def media_upload(self):
        """
        upload a new media using the API
        :return: media_upload_response: json
        """
        try:
            token = self.initiate_token()
            self.upload_token_id = token.id
            file_data = open('penguins.mp4', 'rb')
            resume = False
            final_chunk = True
            resume_at = 0
            result = self.client.uploadToken.upload(self.upload_token_id, file_data, resume, final_chunk, resume_at)
            print("SUCCESS UPLOAD!")
            media_upload_response = json.loads(json.dumps(result, default=lambda result: result.__dict__))
            self.video_exists = True
            return json.dumps(media_upload_response)
        except Exception as e:
            print(e)

    def initiate_token(self):
        """
        create a new upload token for media upload function
        :return: token : str
        """
        upload_token = KalturaUploadToken()
        token = self.client.uploadToken.add(upload_token)
        return token

    def add_entry_to_media(self):
        """
        add the created entry to media
        :return: media_entry_response: json
        """
        try:
            if self.video_exists:
                entry_id = self.entry.id
                resource = KalturaUploadedFileTokenResource()
                resource.token = self.upload_token_id
                result = self.client.media.addContent(entry_id, resource)
                print("ADDED ENTRY TO UPLOADED MEDIA SUCCESSFULLY")
                media_entry_response = json.loads(json.dumps(result, default=lambda result: result.__dict__))
                return json.dumps(media_entry_response)
            else:
                print("Please upload media to add entry")
        except Exception as e:
            print(e)


def main():
    """
    main method invocation
    :return: None
    """
    print("KALTURA VIDEO CLOUD PLATFORM - Customized to Every Video Need")
    print("****************")
    print("ENTER YOUR CHOICE OF OPERATION \n")
    kaltura = KalturaStream(secret, user_id, k_type, partner_id, expiry, privileges,
                            service_url)
    kaltura.initiate_client()
    kaltura.set_session()
    initiate_user_interaction(kaltura)


def initiate_user_interaction(kaltura):
    """
    console GUI
    :param kaltura: Kaltura
    :return: None
    """
    user_input = input("1.LIST ENTRY 2.MEDIA UPLOAD 3.CREATE MEDIA ENTRY \n")
    if user_input == "1":
        input_query = input("Enter the filter tag. For example: quiz\n")
        print(kaltura.list_entries(input_query))
    elif user_input == "2":
        print(kaltura.media_upload())
    elif user_input == "3":
        name = input("Enter media entry name\n")
        description = input("Enter media entry description \n")
        print(kaltura.create_media_entry(name, description))
        add_entry_to_media = input("Do you want add the entry to media? 1.Yes 2.No\n")
        if add_entry_to_media == "1":
            print(kaltura.add_entry_to_media())
        elif add_entry_to_media == "2":
            print("OK")
        else:
            print("Invalid input")
    else:
        print("Invalid input")
    initiate_user_interaction(kaltura)


if __name__ == "__main__":
    main()



