import requests
import urllib.parse
import json

headers = {}


posts_cache = []

class NoUserFoundAtKnownUserDataPathsInTweetDataException(Exception):
    def __init__(self, message: str = "will improve later"):
        self.message = message
        super().__init__(self.message)

class EntryTypeIsNullException(Exception):
    def __init__(self, message: str = "will improve later"):
        self.message = message
        super().__init__(self.message)

def extract_raw_user_data_from_raw_tweet_data(data: dict):
    actual_user_data = None
    data_1 = None
    data_2 = None
    try:
        data_1 = data["core"]["user_results"]["result"]
    except:
        print(f"First data path failed when extracting user data.")
    try:
        data_2 = data["author_community_relationship"]["user_results"]["result"]
    except:
        print(f"Second data path failed when extracting user data.")
    if data_1 is None and data_2 is None:
        raise NoUserFoundAtKnownUserDataPathsInTweetDataException()
    if data_1 == data_2:
        actual_user_data = data_1
    elif data_1 is None:
        actual_user_data = data_2
    elif data_2 is None:
        actual_user_data = data_1
    else:
        print("User data does not match! Defaulting to first known path.")
        actual_user_data = data_1
    return actual_user_data

def generate_twitter_user_object_from_raw_tweet_data(data: dict):
    user_data = extract_raw_user_data_from_raw_tweet_data(data)
    user_object = TwitterUserObject(user_data)
    return user_object

def extract_raw_media_data_items_from_raw_tweet_data(data: dict):
    actual_media_items = None
    media_data_items_1 = None
    media_data_items_2 = None
    base_data: dict = data["legacy"]
    try:
        media_data_items_1 = base_data["entities"]["media"]
    except:
        print("media not found at path 1")
    try:
        media_data_items_2 = base_data["extended_entities"]["media"]
    except:
        print("media not found at path 2")
    if media_data_items_1 is None and media_data_items_2 is None:
        print("no media found on tweet")
    elif media_data_items_1 == media_data_items_2:
        print("both media paths contain the same data. defaulting to 1")
        actual_media_items = media_data_items_1
    elif media_data_items_1 is None:
        print("media path 1 is empty. defaulting to 2")
        actual_media_items = media_data_items_2
    elif media_data_items_2 is None:
        print("media path 2 is empty. defaulting to 1")
        actual_media_items = media_data_items_1
    else:
        path_1_total = len(media_data_items_1)
        path_2_total = len(media_data_items_2)
        if path_1_total >= path_2_total:
            print("media path 1 has more items than media path 2. defaulting to 1")
            actual_media_items = media_data_items_1
        else:
            print("media path 2 has more items than media path 1. defaulting to 2")
            actual_media_items = media_data_items_2
    return actual_media_items

def generate_media_objects_from_raw_tweet_data(data: dict):
    media_items = extract_raw_media_data_items_from_raw_tweet_data(data)
    converted_media_items = [TwitterMediaObject(media_item) for media_item in media_items] if media_items is not None and len(media_items) > 0 else None
    return converted_media_items


class TwitterMediaObject:
    def __init__(self, data: dict):
        self._raw = data
        """
        The raw media data inputted when the object was initially created.
        """
        self.display_url = self._raw.get("display_url", "")
        """
        The url displayed for the media
        """
        self.expanded_url = self._raw.get("expanded_url", "")
        """
        The full media url
        """
        self.id = self._raw.get("id_str", "0")
        """
        The media ID
        """
        self.media_url = self._raw.get("media_url_https", "")
        """
        The direct link to the media
        """
        self.media_type = self._raw.get("type", "unknown")
        """
        The type of media, e.g., photo, video
        """
        self.short_url = self._raw.get("url", "")
        """
        The shortened media url (through twitter's `t.co` shortener)
        """

class TwitterUserObject:
    def __init__(self, data: dict):
        self._raw = data
        """
        The raw user data inputted when the object was initially created.
        """
        self.backend_id: str = self._raw["id"]
        """
        The true use case for this is currently unknown. I'm assuming its simply the user id that's used on the backend servers.
        """
        self.rest_id: str = self._raw["rest_id"]
        """
        This is the id to use when making api calls related to the user
        """
        self.affiliates_highlighted_label: dict = self._raw.get("affiliates_highlighted_label", {})
        """
        No clue what this is used for, but I might experiment with it later
        """
        self._legacy: dict = self._raw["legacy"]
        """
        Legacy data field from api response
        """
        self.display_name: str = self._legacy["name"]
        """
        The user's display name
        """
        self.possibly_sensitive: bool = self._legacy["possibly_sensitive"]
        """
        I'm assuming this is a content tag
        """
        self.profile_image_url: str = self._legacy["profile_image_url_https"]
        """
        The user's pfp url
        """
        self.profile_interstitial_type: str = self._legacy["profile_interstitial_type"]
        """
        No clue what this is
        """
        self.username: str = self._legacy["screen_name"]
        """
        The user's tag, such as @eepyfemboi
        """
        self.want_retweets: bool = self._legacy["want_retweets"]
        """
        My best guess is that this is a flag for people who are spammy about retweets
        """

class TwitterCommunityPostObject:
    def __init__(self, data: dict):
        self._raw: dict = data
        """
        The raw tweet data inputted when the object was initially created.
        """
        self.user: TwitterUserObject = generate_twitter_user_object_from_raw_tweet_data(self._raw)
        """
        The user object of the user who created this tweet.
        """
        self.rest_id: str = self._raw["rest_id"]
        """
        This is the id to use when making api calls related to the tweet
        """
        self.media: list[TwitterMediaObject] | None = generate_media_objects_from_raw_tweet_data(self._raw)
        """
        The media items attached to this tweet
        """
        self._legacy: dict = self._raw["legacy"]
        """
        Legacy data formatting ig
        """
        self.text: str = self._legacy["full_text"]
        """
        The text content of the tweet
        """
        self.user_id: str = self._legacy["user_id_str"]
        """
        The user id of the user who posted this tweet
        """
        self.is_quote: bool = self._legacy["is_quote_status"]
        """
        Whether this is a quote tweet
        """
        self.sensitive: bool = self._legacy.get("possibly_sensitive", False)
        """
        Whether twitter has flagged this tweet as sensitive
        """
        self.possibly_sensitive_editable: bool = self._legacy.get("possibly_sensitive_editable", False)
        """
        No clue.
        """


def get_entry_type_from_raw_content(entry: dict):
    computed_type = ""
    content_typefield_entryType = entry.get("entryType", None)
    content_typefield___typename = entry.get("__typename", None)
    if content_typefield_entryType == content_typefield___typename:
        computed_type = content_typefield_entryType
        if computed_type is None:
            raise EntryTypeIsNullException()
    elif content_typefield_entryType is None:
        #print("Content TYPEFIELD entryType is None. Defaulting to TYPEFIELD __typename.")
        computed_type = content_typefield___typename
    elif content_typefield___typename is None:
        #print("Content TYPEFIELD __typename is None. Defaulting to TYPEFIELD entryType.")
        computed_type = content_typefield_entryType
    else:
        #print(f"Content TYPEFIELD entryType \"{content_typefield_entryType}\" and Content TYPEFIELD __typename \"{content_typefield___typename}\" do not match! Defaulting to TYPEFIELD entryType.")
        computed_type = content_typefield_entryType
    return computed_type

def get_posts_entries_from_raw_timeline_api_response(data: dict):
    raw_instructions = data["data"]["communityResults"]["result"]["ranked_community_timeline"]["timeline"]["instructions"]
    entries = []
    for instruction in raw_instructions:
        if instruction["type"] == "TimelineAddEntries":
            entries = instruction["entries"]
    return entries

def filter_actual_posts_from_api_entries(entries: list):
    real_entries = []
    for entry in entries:
        entry_content = entry["content"]
        entry_type = get_entry_type_from_raw_content(entry_content)
        if entry_type == "TimelineTimelineItem":
            new_content = entry_content["itemContent"]
            timeline_item_type = get_entry_type_from_raw_content(new_content)
            if timeline_item_type == "TimelineTweet" and new_content["tweetDisplayType"] == "Tweet":
                tweet_content = new_content["tweet_results"]["result"]["tweet"]
                real_entries.append(tweet_content)
        elif entry_type != "TimelineTimelineCursor":
            print(f"Encountered unknown entry type: {entry_type}!")
    return real_entries

def process_twitter_community_timeline_api_response_into_twitter_community_post_objects(data: dict):
    post_entries = get_posts_entries_from_raw_timeline_api_response(data)
    actual_posts = filter_actual_posts_from_api_entries(post_entries)
    post_objects = [TwitterCommunityPostObject(post) for post in actual_posts]
    return post_objects


def build_api_url_for_request(post_count: int = 5):
    url_features = {
        "profile_label_improvements_pcf_label_in_post_enabled": True,
        "rweb_tipjar_consumption_enabled": True,
        "responsive_web_graphql_exclude_directive_enabled": True,
        "verified_phone_label_enabled": False,
        "creator_subscriptions_tweet_preview_api_enabled": True,
        "responsive_web_graphql_timeline_navigation_enabled": True,
        "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
        "premium_content_api_read_enabled": False,
        "communities_web_enable_tweet_community_results_fetch": True,
        "c9s_tweet_anatomy_moderator_badge_enabled": True,
        "responsive_web_grok_analyze_button_fetch_trends_enabled": False,
        "responsive_web_grok_analyze_post_followups_enabled": True,
        "responsive_web_jetfuel_frame": False,
        "responsive_web_grok_share_attachment_enabled": True,
        "articles_preview_enabled": True,
        "responsive_web_edit_tweet_api_enabled": True,
        "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
        "view_counts_everywhere_api_enabled": True,
        "longform_notetweets_consumption_enabled": True,
        "responsive_web_twitter_article_tweet_consumption_enabled": True,
        "tweet_awards_web_tipping_enabled": False,
        "creator_subscriptions_quote_tweet_preview_enabled": False,
        "freedom_of_speech_not_reach_fetch_enabled": True,
        "standardized_nudges_misinfo": True,
        "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
        "rweb_video_timestamps_enabled": True,
        "longform_notetweets_rich_text_read_enabled": True,
        "longform_notetweets_inline_media_enabled": True,
        "responsive_web_enhance_cards_enabled": False,
    }

    url_variables = {
        "communityId": "1788526663720210941",
        "count": post_count,
        "displayLocation": "Community",
        "rankingMode": "Recency",
        "withCommunity": True
    }
    
    variables_encoded = urllib.parse.quote(json.dumps(url_variables))
    features_encoded = urllib.parse.quote(json.dumps(url_features))
    
    return f"https://x.com/i/api/graphql/qhyB04iOPDQtpUQjB3C0WQ/CommunityTweetsTimeline?variables={variables_encoded}&features={features_encoded}"

def fetch_posts_from_twitter_community_timeline(post_count: int = 5):
    api_url = build_api_url_for_request(post_count)
    response = requests.get(url = api_url, headers = headers)
    response_raw_data: dict = response.json()
    posts = process_twitter_community_timeline_api_response_into_twitter_community_post_objects(response_raw_data)
    return posts

def fetch_and_print_posts_data(post_count: int = 5):
    posts = fetch_posts_from_twitter_community_timeline(post_count)
    for post in posts:
        print(f"""
Post data for ID: {post.rest_id}
Is Quote: {post.is_quote}
Sensitive: {post.sensitive}
Text: {post.text}
User Dispaly Name: {post.user.display_name}
User Tag: {post.user.username}
Author is NSFW: {post.user.possibly_sensitive}
User want_retweets: {post.user.want_retweets}
User ID: {post.user.rest_id}\n\n
""")


if __name__ == "__main__":
    fetch_and_print_posts_data(10)

