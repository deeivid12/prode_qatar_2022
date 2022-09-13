def querydict_to_dict(query_dict):
	return {k: v[0] if len(v) == 1 else v for k, v in query_dict.lists()}