from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.db.models import F
from django.urls import reverse
from django.views import generic
from django.utils import timezone

from .models import Question
from .models import Choice

# Create your views here.


def index(request):
    """
        Return the last five published questions (not including those set to be
        published in the future).
    """
    print(request.COOKIES)
    latest_questions_list = Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[:5]
    template = loader.get_template("pollsapp/index.html")
    context = {
        "latest_questions_list": latest_questions_list
    }
    return HttpResponse(template.render(context, request))


class QuestionDetailView(generic.DetailView):
    model = Question
    template_name = "pollsapp/detail.html"

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "pollsapp/results.html", {"question": question})


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    print(request.POST)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "pollsapp/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        return HttpResponseRedirect(reverse("pollsapp:results", args=(question_id,)))