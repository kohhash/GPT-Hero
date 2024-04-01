import traceback
import logging
from django.http import HttpResponse
from django.shortcuts import render

from .database_handler import Database
from .essay_rephraser import process_essay
from .ai_detector import copyleaks_detector, gptzero_detector
from .load_resources import ResourceValues

import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Access environment variables
OPEN_API_KEY = os.getenv('OPEN_API_KEY')
PWAID_KEY = os.getenv('PWAID_KEY')

class Rephrase:
    
    def __init__(self, db):
        self.db=db

    def single_essay(self, request):
        form_res=request.POST

        print(f"\nForm response is - {form_res}\n")
        
        if not self.db.validate_key(form_res["openai"]):
            # Print error to frontend
            return HttpResponse("Invalid OpenAPI key provided")
        elif not self.db.validate_key(form_res["prowritingaid"]):
            return HttpResponse("Invalid ProWritingAid API key given")
        else:
            try:
                print("Rephrasing Essay...")

                # check if context field exists
                try:
                    if form_res['context']=='context':
                        context=True
                except Exception:
                        context=False
                print(context)
                # Done

                if form_res["essay"] != "":
                    # print("hello")
                    rephrased_essay = process_essay(
                        form_res["essay"],
                        form_res["approach"],
                        context,
                        int(form_res["randomness"]),
                        form_res["tone"],
                        form_res["difficulty"],
                        form_res["adj"],
                        OPEN_API_KEY, # form_res["openai"],
                        PWAID_KEY, # form_res["prowritingaid"],
                        "nami",
                        form_res["model"],
                        self.db
                    )
                    ai_detection_result = {
                        True: ResourceValues.ai_detection,
                        False: ResourceValues.human_detection,
                    }
                    gptzero_res=ai_detection_result[gptzero_detector(rephrased_essay)]
                    copyleaks_res=ai_detection_result[copyleaks_detector(rephrased_essay)]

                    print(f"Result after is -\nEssay-\n{rephrased_essay}\nGPT-Zero result:\n{gptzero_res}\nCopy leaks result:\n{copyleaks_res}\n")
                    context={
                        "original_essay":form_res["essay"], 
                        "rephrased_essay":rephrased_essay, 
                        "gptzero_res":gptzero_res, 
                        "copyleaks_res":copyleaks_res
                        }
                    return render(request, 'app/result.html', context)
                    
            except Exception as e:
                logging.exception("An error occured in the code")
                traceback.print_exc()
                print(e)
                return HttpResponse(str(e))

    # Function to handle multiple input files
    def multiple_essay(self):
        pass