import zerorpc

config  = {
  "rpc": "tcp://0.0.0.0:3000"
}

class Rpc():
	def get_client(self):
		return zerorpc.Client(config['rpc'], timeout=3000, heartbeat=None)