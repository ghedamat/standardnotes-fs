from api import StandardNotesAPI
from uuid import uuid1

class ItemManager:
    items = {}

    def mapResponseItemsToLocalItems(self, response_items, metadata_only=False):
        DATA_KEYS = ['content', 'enc_item_key', 'auth_hash']

        for response_item in response_items:
            uuid = response_item['uuid']

            if response_item['deleted']:
                if uuid in self.items:
                    del self.items[uuid]
                continue

            response_item['dirty'] = False

            if uuid not in self.items:
                self.items[uuid] = {}

            for key, value in response_item.items():
                if metadata_only and key in DATA_KEYS:
                    continue
                self.items[uuid][key] = value

    def syncItems(self):
        dirty_items = [item for uuid, item in self.items.items() if item['dirty']]

        # remove keys (note: this removes them from self.items as well)
        for item in dirty_items:
            item.pop('dirty', None)
            item.pop('updated_at', None)

        response = self.standard_notes.sync(dirty_items)
        self.mapResponseItemsToLocalItems(response['response_items'])
        self.mapResponseItemsToLocalItems(response['saved_items'], metadata_only=True)

    def getNotes(self):
        notes = {}
        sorted_items = sorted(self.items.items(), key=lambda x: x[1]['created_at'])

        for uuid, item in sorted_items:
            if item['content_type'] == 'Note':
                note = item['content']
                text = note['text'] + '\n'
                count = 0 # used to remove title duplicates

                while True:
                    title = note['title'] + ('' if not count else ' ' + str(count + 1))
                    if title in notes:
                        count += 1
                    else:
                        break

                notes[title] = dict(text=text,
                        created=item['created_at'],
                        modified=item['updated_at'],
                        uuid=item['uuid'])
        return notes

    def writeNote(self, uuid, text):
        item = self.items[uuid]
        item['content']['text'] = text.strip()
        item['dirty'] = True
        self.syncItems()

    def createNote(self, name, time):
        uuid = str(uuid1())
        content = dict(title=name, text='', references=[])
        self.items[uuid] = dict(content_type='Note',
                dirty=True,
                auth_hash=None,
                uuid=uuid,
                created_at=time,
                updated_at=time,
                enc_item_key='',
                content=content)
        return 0

    def deleteNote(self, uuid):
        item = self.items[uuid]
        item['deleted'] = True
        item['dirty'] = True
        self.syncItems()

    def __init__(self, username, password):
        self.standard_notes = StandardNotesAPI(username, password)
        self.syncItems()
