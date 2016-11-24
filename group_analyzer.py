import requests

class GroupAnalyzer():

	def __init__(self, token):
		self.token = token
		self.groups = None
		self.group_id = None
		self.users_data = {}

	def _get_groups(self):
		r = requests.get('https://api.groupme.com/v3/groups?token='+self.token)
		json = r.json()
		data = json['response']

		if len(data) == 0:
		    print("You are not part of any groups.")
		    return
		for i in range(len(data)):
		    print(str(i)+"\'"+data[i]['name']+"\'")
		return data

	def _get_group_id_for_input(self, group_number):
		return self.groups[group_number]['id']

	def _get_messages(self, before_id):
		if len(before_id):
			params = {'before_id' : before_id}
		else:
			params = None
		r = requests.get('https://api.groupme.com/v3/groups/' + self.group_id +'/messages?token='+self.token, params = params)
		json = r.json()
		return json['response']['messages']

	def _analyze(self, group_number):
		for user in self.groups[group_number]['members']:
			user = {'name': user['nickname'], 'id': user['user_id'], 'message-count': 0, 
				'word-count': 0, 'likes-received': 0, 'likes-given': 0}
			self.users_data.update({user['id']: user})
		has_messages = True
		while(has_messages):
			messages = self._get_messages('')
			for message in messages:
				sender_id = message['user_id']
				self.users_data[sender_id]['message-count'] += 1
				self.users_data[sender_id]['word-count'] += len(message['text'].split())
				for like_id in message['favorited_by']:
					self.users_data[like_id]['likes-given'] += 1
					self.users_data[sender_id]['likes-received'] += 1
			print(self.users_data)
			has_messages = False



	def analyze(self):
		self.groups = self._get_groups();
		try:
			group_number = int(input("Enter the number of the group you would like to analyze:"))
			self.group_id = self._get_group_id_for_input(group_number)
			self._analyze(group_number)
		except ValueError:
			print("Not a number")

def main():
    ga = GroupAnalyzer("dcWvMk4nP4YnBR1p12ImCK4Qn8vhrVzM8xUCnCwt")
    ga.analyze()


if __name__ == '__main__':
    main()