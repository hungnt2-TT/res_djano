from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


def paginate_data(data, page_size, page):
    paginator = Paginator(data, int(page_size))
    try:
        data = paginator.page(page)
    except PageNotAnInteger:
        data = paginator.page(1)
    except EmptyPage:
        data = paginator.page(paginator.num_pages)
    return data

