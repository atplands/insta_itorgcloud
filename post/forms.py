from django import forms
from post.models import Post, Tag
from multiupload.fields import MultiFileField, MultiImageField

from django.core.files import File


class NewPostform(forms.ModelForm):
    # content = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=True)
    
    # picture = forms.ImageField(required=True)  #  commented
    caption = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Caption'}), required=True)
    tags = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Tags | Separate with comma'}), required=True)

    class Meta:
        model = Post
        fields = [ 'caption', 'tags'] # 'picture'



class EditPostForm(forms.ModelForm):
    # picture = forms.ImageField(required=True)
    caption = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Caption'}), required=True)
    tags = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Tags | Separate with comma'}), required=True)
    #picture = forms.ImageField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)
    # images = forms.ImageField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)
    class Meta:
        model = Post
        fields = ['caption',] # 'picture'       
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if self.instance.pk:
            self.fields['tags'].initial = ','.join(
                tag.title for tag in self.instance.tags.all()
            )
            

            

            