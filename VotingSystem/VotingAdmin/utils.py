from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def broadcast_vote_update(candidate_id, votes):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "election_results",
        {
            "type": "election_results_update",
            "text": {"candidate_id": candidate_id, "votes": votes},
        },
    )