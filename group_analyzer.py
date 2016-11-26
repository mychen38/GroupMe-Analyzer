import requests
import json
import argparse

class GroupAnalyzer():

	def __init__(self, token):
		self.token = token
		self.group = None
		self.group_id = None
		self.users_data = {}

	def _get_group(self):
		r = requests.get('https://api.groupme.com/v3/groups?token='+self.token)
		json = r.json()
		data = json['response']

		if len(data) == 0:
		    print("You are not part of any groups.")
		    return
		for i in range(len(data)):
		    print(str(i)+"\'"+data[i]['name']+"\'")

		group_number = int(input("Enter the number of the group you would like to analyze:"))

		return data[group_number]

	def _get_group_id_for_input(self):
		return self.group['id']

	def _get_messages(self, before_id):
		if len(before_id):
			params = {'before_id' : before_id, 'limit' : 100}
		else:
			params = {'limit' : 100}
		r = requests.get('https://api.groupme.com/v3/groups/' + self.group_id +'/messages?token='+self.token, params = params)
		json = r.json()
		return json['response']['messages']

	def _analyze(self):
		has_messages = True
		before_id = ''
		count = 0
		#20 Messages per request
		while(has_messages):
			messages = self._get_messages(before_id)
			count += len(messages)
			for message in messages:
				if 'event' in message:
					if 'user' in message['event']['data']:
						sender_id = str(message['event']['data']['user']['id'])
					elif 'adder_user' in message['event']['data']:
						sender_id = str(message['event']['data']['adder_user']['id'])
					elif 'remover_user' in message['event']['data']:
						sender_id = str(message['event']['data']['remover_user']['id'])
				elif message['user_id'] != 'system':
					sender_id = message['user_id']
					self.users_data[sender_id]['message-count'] += 1
					if isinstance(message['text'], str):
						self.users_data[sender_id]['word-count'] += len(message['text'].split())
				for like_id in message['favorited_by']:
					self.users_data[like_id]['likes-given'] += 1
					self.users_data[sender_id]['likes-received'] += 1
			before_id = messages[-1]['id']
			has_messages = False if len(messages) < 100 else True



	def analyze(self):
		try:
			self.group = self._get_group()
			for user in self.group['members']:
				user = {'name': user['nickname'], 'id': user['user_id'], 'message-count': 0, 
					'word-count': 0, 'likes-received': 0, 'likes-given': 0}
				self.users_data.update({user['id']: user})
			self.group_id = self._get_group_id_for_input()
			self._analyze()
			print(json.dumps(self.users_data))
		except ValueError:
			print("Not a number")

def main():
	parser = argparse.ArgumentParser(description='''GroupMe Analyzer''')
	parser.add_argument('token', help='GroupMe API Access token: https://dev.groupme.com/')
	args = parser.parse_args()

	ga = GroupAnalyzer(args.token)
	ga.analyze()


if __name__ == '__main__':
    main()