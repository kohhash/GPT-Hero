import configparser
import bleach
from django.conf import settings
from configurations.configuration import Configuration

import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Access environment variables
STRIPE_API_KEY = os.getenv('STRIPE_API_KEY')
STRIPE_WEBHOOK = os.getenv('STRIPE_WEBHOOK')

# config_file = r"D:\coding\project_coding\django_GPT\GPTHero\app\data\config-1.ini"
config = configparser.ConfigParser()
config_file = Configuration.DefaultValues.config_file_path


def read_config():
    config.read(config_file, encoding="utf-8")


def generate_constant():
    gc = lambda group: lambda key: config.get(group, key)
    h = gc("help")
    g = gc("general")
    p = gc("placeholders")
    t = gc("tooltip")
    b = gc("button")
    l = gc("labels")
    d = gc("default")
    e = gc("errors")
    a = gc("api")
    bi = gc("billing")

    class StringConstants:

        # database_file = r"D:\coding\project_coding\django_GPT\GPTHero\db.sqlite3"
        database_file = Configuration.DefaultValues.database_path

        # Info boxes
        help_conservative_approach = h("conservative_approach")
        help_creative_approach = h("creative_approach")
        help_original_essay = h("original_essay")
        help_advanced_options = h("advanced_options")

        # General
        title = g("title")
        spinner = g("spinner")
        alr_login = g("already_logged_in")
        sucs_login = g("successful_login")
        login_title = g('login_title')
        advanced_options = g('advanced_options')
        rephrased_essay_input_header = g('rephrased_essay_header')
        rephrased_essay_file_header = g('rephrased_essay_file_header')
        gptzero = g("gptzero")
        copyleaks = g("copyleaks")
        rephrased_files_tabs_title = g("rephrased_essay_files_tabs_title")
        ai_detection = g("ai_detection")
        human_detection = g("human_detection")
        admin_header = g("admin_header")
        essay_history_header = g("essay_history_header")
        register_title = g("register_title")
        register_user_created_success = g("user_created_success")
        config_header = g("config_header")
        user_count = g("user_count")
        token = g("token")
        invite_link = g("invite_link")

        # Placeholders
        openai_api_key_ph = p("openai_api_key")
        prowritingaid_api_key_ph = p("prowritingaid_api_key")
        essay_ph = p("essay")
        login_username_ph = p("login_username")
        login_password_ph = p("login_password")
        register_username_ph = p("register_username")
        register_password_ph = p("register_password")
        register_confirm_password_ph = p("register_confirm_password")
        admin_username_ph = p("admin_username")

        # Tooltips
        approach_tooltip = t("approach")
        context_tooltip = t("context")
        randomness_tooltip = t("randomness")
        multiple_essays_tooltip = t("multiple_essays")
        tone_tooltip = t("tone")
        difficulty_tooltip = t("difficulty")
        additional_adjectives_tooltip = t("additional_adjectives")

        # Buttons
        rephrase_essay_button = b("rephrase_essay")
        login_button = b("login")
        register_button = b("register")
        set_button = b("set")
        logout_button = b("log_out")
        add_button = b("add")

        # Labels
        context_label = l("context_option")
        randomness_label = l("randomness_option")
        tone_label = l("tone_option")
        difficulty_label = l("difficulty_option")
        additional_adjectives_label = l("additional_adjectives")
        approach_label = l("approach_option")
        approach_choice_creative_label = l("approach_option_choice_creative")
        approach_choice_conservative_label = l("approach_option_choice_conservative")
        multiple_essays_label = l("multiple_essays_option")
        config_file_upload_label = l("config_file_upload")

        # Defaults

        openai_api_key_default_val = d("openai_api_key_default")
        prowritingaid_api_key_default_val = d("prowritingaid_api_key_default")
        openai_api_key_default_replacement_placeholder = d("openai_api_default_key_placeholder")
        prowriting_api_key_default_replacement_placeholder = d("prowritingaid_api_default_key_placeholder")
        approach_default_val = d("approach_option")
        context_default_val = d("context_option")
        randomness_default_val = d("randomness_option")
        tone_default_val = d("tone_option")
        difficulty_default_val = d("difficulty_option")
        additional_adjectives_default_val = d("additional_adjectives_option")


        # Errors

        username_does_not_exist_error = e("username_does_not_exist")
        invalid_password_error = e("invalid_password")
        invalid_username_error = e("invalid_password")
        incorrect_login_details_error =  e("incorrect_login_details")
        openai_error_prefix = e("openai_error_prefix")
        prowritingaid_prefix = e("prowritingaid_error_prefix")
        unknown_error = e("unknown_error")
        free_limit_over_error = e("free_limit_over")

        prompt_description_api = a("prompt_description")
        user_description_api = a("user_description")
        rephrase_essay_description = a("rephrase_essay_description")
        openaiapikey_examples = a("openaiapikey_example")
        prowritingaidapikey_example = a("prowritingaidapikey_example")
        essay_example = a("essay_example")

        # billing

        stripe_key = STRIPE_API_KEY
        stripe_wh_endpoint = STRIPE_WEBHOOK
        free_limit = bi("free_limit")



    return StringConstants


def load_config():
    global ResourceValues
    try:
        read_config()
        ResourceValues = generate_constant()

    except Exception as e:
        print("Exception occured:", e)
        print("Using default config")
        config.read("default-config.ini", encoding="utf-8")
        ResourceValues = generate_constant()
    return ResourceValues


def refresh_config():
    print("Refreshing config")
    print("Refreshed title:", config.get("general", "title"))
    load_config()


def get_string_constants():
    return ResourceValues

def get_default_key(givenval, default_val, default_val_placeholder):
    print("Given val:", givenval, "Default val:", default_val, "Default val placeholder:", default_val_placeholder)
    if default_val and (givenval == default_val_placeholder or (                          # Check if there is default value. If there is default value, if placeholder value is None or if placeholder value is equal to given value.
            default_val_placeholder is None and (givenval is None or givenval == ""))):
        givenval = default_val
    print("Final givenval:", givenval)
    return givenval


def get_default_openai_key(givenval):
    return get_default_key(givenval, ResourceValues.openai_api_key_default_val, ResourceValues.openai_api_key_default_replacement_placeholder)


def get_default_prowritingaid_key(givenval):
    return get_default_key(givenval, ResourceValues.prowritingaid_api_key_default_val, ResourceValues.prowriting_api_key_default_replacement_placeholder)

def validate_username(username):
    if len(username) <= 4:
        raise Exception("Username should be more than 4 characters")
    return bleach.clean(username, tags=[])

def validate_password(password):
    if len(password) <= 6:
        raise Exception("Password should be more than 6 characters")
    return bleach.clean(password, tags=[])
# ResourceValues = None
ResourceValues = load_config()


class Approach:
    creative = ResourceValues.approach_choice_creative_label
    conservative = ResourceValues.approach_choice_conservative_label