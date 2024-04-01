from ProWritingAidSDK.rest import ApiException
import ProWritingAidSDK

# def set_api_key(api_key):
#     global configuration
#

def fix_sentence(wrong_sent, api_key):
    configuration = ProWritingAidSDK.Configuration()
    configuration.host = 'https://api.prowritingaid.com'
    configuration.api_key['licenseCode'] = api_key
    # To get an API code with 500 test credits go to https://prowritingaid.com/en/App/Api

    # create an instance of the API class
    api_instance = ProWritingAidSDK.TextApi(ProWritingAidSDK.ApiClient('https://api.prowritingaid.com'))

    try:
        api_request = ProWritingAidSDK.TextAnalysisRequest(wrong_sent,
                                                           ["grammar", "complex"],
                                                           "General",
                                                           "en")
        api_response = api_instance.post(api_request)

    except ApiException as e:
        print("Exception when calling TextAnalysisRequest->get: %s\n", e)
        raise ApiException("Exception when calling TextAnalysisRequest->get")
    tags = api_response.result.tags
    correct_sentence = wrong_sent
    # Apply all the tags to the original string to get a corrected string
    # Important to work through the tags backward to that indexes don't change
    for tag in reversed(tags):
        if len(tag.suggestions) <= 0:
            continue
        replacement = '' if tag.suggestions[0] == '(omit)' else tag.suggestions[0]
        correct_sentence = correct_sentence[0:tag.start_pos] + replacement + correct_sentence[tag.end_pos + 1:]
    return correct_sentence
