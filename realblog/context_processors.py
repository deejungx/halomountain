from .models import BlogCategory, BlogPageTag


# Blog Category Context for base template
def catgry(request):
    CATEGORIES = BlogCategory.objects.all()
    response = {'CATEGORIES': CATEGORIES, }
    return response


# Blog Tag Context for base templates
def tagz(request):
    new_tag_list = []
    TAGS = BlogPageTag.objects.all().order_by('-tag')[:15]
    for elmnt in TAGS:
        if elmnt.tag not in [t.tag for t in new_tag_list]:
            new_tag_list.append(elmnt)
        else:
            pass
    TAGS = new_tag_list
    response = {'TAGS': TAGS, }
    return response
