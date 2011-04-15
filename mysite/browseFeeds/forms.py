from django import forms

class AddFeedForm(forms.Form):
    url = forms.URLField(label='Feed URL')
    category = forms.ChoiceField()
    subscribe = forms.BooleanField(required=False)

    def __init__(self, categories, *args, **kwargs): 
        super(AddFeedForm, self).__init__(*args, **kwargs)
        self.fields['category'].choices = [[x,x] for x in categories]

class EditFeedForm(forms.Form):
    feed_name = forms.CharField()
    category = forms.ChoiceField()

    def __init__(self, categories, *args, **kwargs): 
        super(EditFeedForm, self).__init__(*args, **kwargs)
        self.fields['category'].choices = [[x,x] for x in categories]

class AddCategoryForm(forms.Form):
    category = forms.CharField()

class SubscribeFeedForm(forms.Form):
    category_choice = forms.ChoiceField()

    def __init__(self, categories, *args, **kwargs): 
        super(SubscribeFeedForm, self).__init__(*args, **kwargs)
        self.fields['category_choice'].choices = [[x,x] for x in categories]

class ShareStoryForm(forms.Form):
    friends_choice = forms.MultipleChoiceField()

    def __init__(self, friends, *args, **kwargs): 
        super(ShareStoryForm, self).__init__(*args, **kwargs)
        self.fields['friends_choice'].choices = [[x.user_uuid,x] for x in friends]





