# TODO: enable payment handler functionality - Line 204, 249

import os
import traceback

import openai
import json
import time
import tiktoken

from .grammar_check import fix_sentence, ApiException
from .load_resources import Approach, ResourceValues
# from payment_handler import can_rephrase, report_usage
# import stripe
# from .database_handler import Database

# stripe.api_key = ResourceValues.stripe_key

encoder = tiktoken.encoding_for_model("text-davinci-003")


def count_tokens(text):
    return len(encoder.encode(text))


def prompt_generator(
    text_type="sentence",
    tone="formal",
    previous_text=None,
    approach="creative",
    perplexity="very high",
    difficulty="common and easy to understand",
    additional_content_comments="precise, concise, logical and easy to read",
    start_with=None,
):
    prompt = ""
    if type(previous_text) == str:
        prompt += f"Previous {text_type} for context: {previous_text}\n"
    if approach == "creative":
        prompt += f"Rephrase the following {text_type} to create {perplexity} perplexity. Use {difficulty} words and the rephrased content should be {additional_content_comments}. Use {tone} tone."
    else:
        prompt += f"Rephrase the following {text_type} a little:\n"
    if start_with is not None:
        print("Adding start with")
        prompt += f" Strictly Start with {start_with}."
    prompt += f" Here is the {text_type} to rephrase:\n"
    return prompt


def rephrase_text_gpt(
    model,
    text,
    text_type="sentence",
    randomness=0.6,
    presence_penalty=0,
    logit_bias=None,
    tone="formal",
    start_with=None,
    api_key=None,
    **kwargs,
):
    """Rephrase text using GPT to create more randomness to prevent detection"""

    prompt = (
        prompt_generator(
            text_type=text_type, tone=tone, start_with=start_with, **kwargs
        )
        + text
    )
    if model=="GPT-3":
        model_key="gpt-3.5-turbo"
    elif model=="GPT-4":
        model_key="gpt-4"
    result = openai.ChatCompletion.create(
        model=model_key,
        api_key=api_key,
        messages=[{'role': 'user', 'content': prompt}],
        max_tokens=4000
        - int(
            (len(prompt) / 4) + 5
        ),  # Adjust max_tokens according to prompt size by subtracting 1/4th of each character in prompt along with an additional 5 for extra measures.
        temperature=randomness,
        presence_penalty=presence_penalty,
    )
    rephrased_sentence = result["choices"][0]["message"]["content"]
    print(f"Printing from rephrase_text_gpt function - {rephrased_sentence}\n")
    if start_with:
        rephrased_sentence = rephrased_sentence.replace(start_with, "")
        while rephrased_sentence.startswith("$"):
            rephrased_sentence = rephrased_sentence[1:]
    return rephrased_sentence


# def json_save(filepath, obj):
#     with open(filepath, "w") as file:
#         json.dump(obj, file)


def rephrase_text_by_paragraph(
    text,
    para_splitter="\n\n",
    use_pevious_for_context=True,
    randomness=1.2,
    model="GPT-3",
    approach="creative",    
    **kwargs,
):
    """Rephrase a text containing any number of sentences."""

    text = text.replace("\r", "\n")
    paragraphs = text.split(para_splitter)  # Split by paragraph
    rephrased_paragraphs = []
    for i, paragraph in enumerate(paragraphs):
        print(f"\nParagraph - {i}: \n", paragraph)
        if use_pevious_for_context and i > 0:
            rephrased_paragraph = rephrase_text_gpt(
                model,
                paragraph,
                "paragraph",
                previous_text=paragraphs[i - 1],
                randomness=randomness,
                approach=approach,
                **kwargs,
            )
        else:
            rephrased_paragraph = rephrase_text_gpt(
                model,
                paragraph,
                "paragraph",
                randomness=randomness,
                approach=approach,
                **kwargs,
            )
        rephrased_paragraph = rephrased_paragraph.strip()
        print("\nRephrased paragraph - \n")
        print(rephrased_paragraph)
        rephrased_paragraphs.append(rephrased_paragraph)
    print(*rephrased_paragraphs, sep="\n")
    return "\n\n".join(rephrased_paragraphs)


# def rephrase_from_json(
#     question_essays_filename="essays_data.json",
#     rephrased_essays_filename="rephrased_data.json",
# ):
#     # Read essays from question file, remove them from question file,
#     # and insert them in rephrased file with rephrased essays

#     question_essays = []
#     rephrased_essays = []
#     if not os.path.exists(question_essays_filename):
#         raise Exception("No question essays provided")
#     with open(question_essays_filename, "r") as question_essay_file:
#         question_essays = json.load(question_essay_file)
#     if os.path.exists(rephrased_essays_filename):
#         with open(rephrased_essays_filename, "r") as rephrased_essays_file:
#             rephrased_essays = json.load(rephrased_essays_file)

#     while len(question_essays) > 0:
#         print("Rephrasing essay no. ", len(question_essays))
#         question_essay = question_essays.pop()
#         rephrased_essay = rephrase_text_by_paragraph(question_essay)
#         rephrased_essays.append(
#             {"org_text": question_essay, "rephrased_text": rephrased_essay}
#         )
#         json_save(rephrased_essays_filename, rephrased_essays)
#         json_save(question_essays_filename, question_essays)
#         time.sleep(60)


# def analyse_different_temperatures(essays):
#     temperatures = [
#         1.2,
#     ]
#     for ti, temperature in enumerate(temperatures):
#         for i, essay in enumerate(essays):
#             print(f"Generated rephrased Essay {i}. for temperature {temperatures[ti]}")
#             rephrased_essay = rephrase_text_by_paragraph(
#                 essay, randomness=temperature, approach="minimal"
#             )
#             print(rephrased_essay)
#             print("=" * 10)
#             time.sleep(120)


def process_essay(
    essay,
    approach,
    context,
    randomness,
    tone,
    difficulty,
    additional_adjectives,
    openaiapikey,
    pwaidapikey,
    username,
    model,
    # db
):
    # openai.api_key = openaiapikey

    tokens_usage_for_query = count_tokens(essay)

    # if not can_rephrase(username, tokens_usage_for_query):
    #     raise Exception("You have run out of credits. Please apply for more credits!")

    try:
        randomness = 0.5 + randomness / 10

        print("Processing essay..\n", essay)
        if approach == Approach.creative:
            rephrased_essay = rephrase_text_by_paragraph(
                essay,
                use_pevious_for_context=context,
                randomness=randomness,
                approach=approach.lower(),
                # start_with="$_$",
                tone=tone,
                difficulty=difficulty,
                additional_content_comments=additional_adjectives,
                api_key=openaiapikey,
                model=model
            )
        else:
            rephrased_essay = rephrase_text_by_paragraph(
                essay,
                use_pevious_for_context=context,
                randomness=randomness,
                approach=approach.lower(),
                # start_with="$_$",
                api_key=openaiapikey,
                model=model
            )
        print("\nRephrase essay per-fix:\n", rephrased_essay)
        rephrased_essay = fix_sentence(rephrased_essay, pwaidapikey)

    except Exception as e:
        traceback.print_exc()
        if isinstance(e, openai.error.OpenAIError):
            raise Exception(ResourceValues.openai_error_prefix + " " + str(e))
        elif isinstance(e, ApiException):
            raise Exception(ResourceValues.prowritingaid_prefix + " " + str(e))
        else:
            raise Exception(ResourceValues.unknown_error)

    # db.insert_essay(essay, rephrased_essay, username)
    # if db.is_subscribed(username):
        # report_usage(username, tokens_usage_for_query)
    return rephrased_essay


# if __name__ == "__main__":
#     with open("academic_essays.json", "r") as file:
#         essays = json.load(file)
#     essay = essays[3]
#     print(essay)
#     print(rephrase_text_by_paragraph(essay))
#     # analyse_different_temperatures(essays)
