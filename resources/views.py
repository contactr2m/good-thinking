from django.db.models import Q

from itertools import chain

from django.http import JsonResponse, HttpResponse

from resources.models.tags import TopicTag, IssueTag, ReasonTag, ContentTag
from resources.models.helpers import (
    create_tag_combiner, count_likes, filter_tags,
    get_tags, get_order, get_relevance, base_context
)

from django.core import serializers
from django.template import loader
from django.template.loader import render_to_string

from django.apps import apps

from urllib.parse import parse_qs

from django.core.paginator import Paginator

import requests


def get_json_data(request):
    try:
        query = request.GET.urlencode()
        slug = parse_qs(query)['slug'][0]
    except:
        slug = ''

    data = get_data(request, slug=slug)
    json_data = {}

    resources = list(
        map(
            lambda r: render_to_string(
                'resources/short_resource.html',
                {'page': r},
                request=request
            ),
            data['resources']
        )
    )

    tips = list(
        map(
            lambda r: render_to_string(
                'resources/tip.html',
                {'page': r},
                request=request
            ),
            data['tips']
        )
    )

    assessments = list(
        map(
            lambda r: render_to_string(
                'resources/assessment.html',
                {'page': r},
                request=request
            ),
            data['assessments']
        )
    )

    json_data['resources'] = list(chain(resources, assessments))
    json_data['tips'] = tips

    for d in data:
        if d != 'resources' and d != 'tips':
            try:
                json_data[d] = serializers.serialize('json', data[d])
            except:
                json_data[d] = data[d]

    return JsonResponse(json_data)


def get_data(request, **kwargs):
    ResourcePage = apps.get_model('resources', 'resourcepage')
    Tip = apps.get_model('resources', 'tip')
    Assessment = apps.get_model('resources', 'assessment')

    data = kwargs.get('data', {})
    slug = kwargs.get('slug')
    query = request.GET.get('q')
    Home = apps.get_model('resources', 'home')

    tag_filter = request.GET.getlist('tag')
    issue_filter = kwargs.get('path_components', request.GET.getlist('q1'))
    content_filter = request.GET.getlist('q3')
    reason_filter = request.GET.getlist('q2')
    topic_filter = request.GET.getlist('topic')

    if request.GET.get('order'):
        resource_order = request.GET.get('order')
    else:
        resource_order = "default"

    if slug != 'home':
        topic_filter = slug

    issue_tags = get_tags(IssueTag)
    content_tags = get_tags(ContentTag)
    reason_tags = get_tags(ReasonTag)
    topic_tags = get_tags(TopicTag)

    selected_tags = list(chain(
        tag_filter,
        issue_filter,
        content_filter,
        reason_filter,
    ))

    num_likes = 'select ' \
        + 'count(like_value) from likes_likes ' \
        + 'where resource_id = resources_resourcepage.page_ptr_id ' \
        + 'and like_value = %s'

    resources = get_order(ResourcePage.objects.all().annotate(
        score=(count_likes(1) - count_likes(-1)),
        relevance=(get_relevance(selected_tags))
    ), resource_order).live()

    resources = resources.extra(
        select={'number_of_likes': num_likes},
        select_params=([1])
    )

    resources = resources.extra(
        select={'number_of_dislikes': num_likes},
        select_params=([-1])
    )

    if 'ldmw_session' in request.COOKIES:
        cookie = request.COOKIES['ldmw_session']
        liked_value = 'select ' \
            + 'like_value from likes_likes where ' \
            + 'resource_id  = resources_resourcepage.page_ptr_id '\
            + 'and user_hash = %s'
        resources = resources.extra(
            select={'liked_value': liked_value},
            select_params=([cookie])
        )
    else:
        cookie = ''

    if 'ldmw_visited_resources' in request.COOKIES:
        data['visited'] = get_visited_resources(
            visited_cookie=request.COOKIES['ldmw_visited_resources'],
            user_cookie=cookie
        )

    if topic_filter:
        (
            filtered_issue_tags,
            filtered_reason_tags,
            filtered_content_tags,
        ) = filter_tags(resources, topic_filter)

        if filtered_issue_tags:
            data['issue_tags'] = get_tags(
                IssueTag,
                filtered_tags=filtered_issue_tags
            ).values()

        if filtered_content_tags:
            data['content_tags'] = get_tags(
                ContentTag,
                filtered_tags=filtered_content_tags
            ).values()

        if filtered_reason_tags:
            data['reason_tags'] = get_tags(
                ReasonTag,
                filtered_tags=filtered_reason_tags
            ).values()

        excluded_tags = (
            Home.objects.get(slug=topic_filter).specific.exclude_tags.all()
        )
    else:
        data['issue_tags'] = issue_tags.values()
        data['content_tags'] = content_tags.values()
        data['reason_tags'] = reason_tags.values()
        excluded_tags = []

    if (tag_filter):
        resources = resources.filter(
            Q(content_tags__name__in=tag_filter) |
            Q(reason_tags__name__in=tag_filter) |
            Q(issue_tags__name__in=tag_filter) |
            Q(topic_tags__name__in=tag_filter)
        ).distinct()

    tips = filter_resources(
        Tip.objects.all(),
        tag_filter=tag_filter,
        issue_filter=issue_filter,
        topic_filter=topic_filter,
        query=query
    )

    assessments = filter_resources(
        Assessment.objects.all(),
        tag_filter=tag_filter,
        issue_filter=issue_filter,
        topic_filter=topic_filter,
        query=query
    )

    resources = filter_resources(
        resources,
        tag_filter=tag_filter,
        issue_filter=issue_filter,
        topic_filter=topic_filter,
        query=query
    ).filter(~Q(page_ptr_id__in=list(chain(tips, assessments))))

    paged_resources = get_paged_resources(request, resources)

    combine_tags = create_tag_combiner(excluded_tags)

    filtered_resources = map(combine_tags, paged_resources)

    data['landing_pages'] = Home.objects.filter(~Q(slug="home")).live()
    data['resources'] = filtered_resources
    data['tips'] = tips
    data['assessments'] = assessments
    data['resource_count'] = resources.count() + tips.count()
    data['topic_tags'] = topic_tags.values()
    data['selected_topic'] = topic_filter
    data['selected_tags'] = selected_tags

    return data


def get_visited_resources(**kwargs):
    ResourcePage = apps.get_model('resources', 'resourcepage')
    visited_cookie = kwargs.get('visited_cookie')
    user_cookie = kwargs.get('user_cookie')

    if visited_cookie:
        visited_ids = filter(lambda x: x != "", visited_cookie.split(','))
    else:
        visited_ids = []

    liked_value = """select like_value from likes_likes
    where resource_id = resources_resourcepage.page_ptr_id
    and user_hash = %s"""
    visited_resources = ResourcePage.objects\
        .filter(id__in=visited_ids)\
        .extra(
          select={'liked_value': liked_value},
          select_params=([user_cookie])
        )

    return visited_resources


def get_paged_resources(request, resources):
    paginator = Paginator(resources, 3)

    try:
        if request.GET.get('page') == 'initial':
            paged_resources = paginator.page(1)
        elif request.GET.get('page') == 'remainder':
            try:
                current_page = paginator.page(2)
                paged_resources = chain(current_page)

                while current_page.has_next():
                    current_page = paginator.page(
                        current_page.next_page_number()
                    )
                    paged_resources = chain(paged_resources, current_page)
            except:
                paged_resources = []
        else:
            paged_resources = resources
    except:
        paged_resources = resources

    return paged_resources


def filter_resources(resources, **kwargs):
    tag_filter = kwargs.get('data')
    issue_filter = kwargs.get('issue_filter')
    topic_filter = kwargs.get('topic_filter')
    query = kwargs.get('query')

    if (tag_filter):
        resources = resources.filter(
            Q(content_tags__name__in=tag_filter) |
            Q(reason_tags__name__in=tag_filter) |
            Q(issue_tags__name__in=tag_filter) |
            Q(topic_tags__name__in=tag_filter)
        ).distinct()

    if (issue_filter):
        resources = resources\
            .filter(issue_tags__name__in=issue_filter)\
            .distinct()

    if (topic_filter):
        resources = resources\
            .filter(topic_tags__name=topic_filter)\
            .distinct()

    if (query):
        resources = resources.search(query)

    return resources


def assessment_controller(self, request, **kwargs):
    params = request.POST

    answers = filter(lambda p: p[:2] == "Q_", params)

    prms = {}

    for a in answers:
        if len(a.split("_")) == 3:
            prms[a.split("_")[2]] = params.get(a)
        else:
            prms[params.get(a)] = ""

    if not (params.get("member_id") and params.get("traversal_id")):
        r = requests.get(
            "http://apps.expert-24.com/WebBuilder/"
            + "TraversalService/Member?callback=raw&@usertype=300"
        )

        response = r.json()
        member_id = response["Table"][0]["MemberID"]
        traversal_id = response["Table"][0]["TraversalID"]
    else:
        member_id = params.get("member_id")
        traversal_id = params.get("traversal_id")

    algo_id = self.algorithm_id
    node_id = 0

    if params.get("node_id"):
        node_id = params.get("node_id")

    if params.get("algo_id"):
        algo_id = params.get("algo_id")

    if params.get("previous"):
        direction = params.get("previous")
    elif params.get("q_info"):
        direction = "Rerender"
        node_type_id = 32
        asset_id = params.get("q_info")
    elif params.get("a_info"):
        direction = "Rerender"
        node_type_id = 64
        asset_id = params.get("a_info")
    elif params.get("return_summary"):
        direction = params.get("return_summary")
    else:
        direction = "Next"

    url = f"http://apps.expert-24.com/WebBuilder/TraversalService/" \
        + f"{direction}/{traversal_id}/{member_id}/" \
        + f"{algo_id}/{node_id}?callback=raw"

    for p in prms:
        url += f"&{p}={prms[p]}"

    r2 = requests.get(url)

    template = loader.get_template(
        "resources/assessment/server-assessment.html"
    )

    context = r2.json()

    context["member_id"] = member_id
    context["traversal_id"] = traversal_id

    try:
        context['parent'] = self.get_parent().slug
        context['slug'] = self.slug
    except:
        context['parent'] = None
        context['slug'] = None

    context['heading'] = self.heading
    context['body'] = self.body

    if params.get("q_info") or params.get("a_info"):
        context["info"] = requests.get(
            f"http://apps.expert-24.com/WebBuilder/TraversalService/Info/"
            + f"{traversal_id}/{member_id}?callback=raw&@NodeTypeID="
            + f"{node_type_id}&@AssetID={asset_id}"
        ).json()

    return HttpResponse(
        template.render(context=base_context(context), request=request)
    )


def assessment_summary_controller(request, **kwargs):
    template = loader.get_template(
        "resources/assessment/assessment-summary.html"
    )

    traversal_id = request.POST.get("traversal_id")
    member_id = request.POST.get("member_id")

    context = requests.get(
        f"http://apps.expert-24.com/WebBuilder/TraversalService/Summary/"
        + f"{traversal_id}/{member_id}?callback=raw"
    ).json()

    context["member_id"] = member_id
    context["traversal_id"] = traversal_id
    context["node_id"] = request.POST.get("node_id")
    context["algo_id"] = request.POST.get("algo_id")
    context["parent"] = request.POST.get("parent")
    context["slug"] = request.POST.get("slug")

    return HttpResponse(
        template.render(context=base_context(context), request=request)
    )
