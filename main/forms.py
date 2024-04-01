from django import forms

class RephraseForm(forms.Form):
    approach = forms.ChoiceField(
        label="Choose Approach",
        choices=[("Conservative", "Conservative"), ("Creative", "Creative")],
        initial="Creative",
        widget=forms.RadioSelect
    )
    model = forms.ChoiceField(
        label="Choose Model",
        choices=[("GPT-3", "GPT-4"), ("GPT-4", "GPT-3")],
        initial="GPT-4",
        widget=forms.RadioSelect
    )
    context = forms.BooleanField(label="Context", required=False, initial=True)
    randomness = forms.IntegerField(label="Select randomness", min_value=1, max_value=10, initial=5)
    tone = forms.CharField(label="Tone", max_length=100, initial="Newspaper")
    difficulty = forms.CharField(label="Difficulty", max_length=100, initial="Easy to understand, very common")
    adj = forms.CharField(label="Additional Adjectives", max_length=100, initial="Concise and precise, to the point")
    myfile = forms.FileField(label="Select a file", required=False)
    essay = forms.CharField(label="Enter essay to be rephrased", widget=forms.Textarea(attrs={"cols": "30", "rows": "10"}))

class SetKeyForm(forms.Form):

    openai_api_key = forms.CharField(label="OpenAI API key", max_length=100, required=False)
    prowritingaid_api_key = forms.CharField(label="ProWritingAid API key", max_length=100, required=False)