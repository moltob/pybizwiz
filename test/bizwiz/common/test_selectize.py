import pytest
from django.core import exceptions

from bizwiz.articles.models import Article
from bizwiz.common.selectize import ModelMultipleChoiceTextField


def test__model_multiple_choice_text_field__to_python__empty():
    field = ModelMultipleChoiceTextField(queryset=None)
    assert field.to_python('') == []


def test__model_multiple_choice_text_field__to_python__single():
    field = ModelMultipleChoiceTextField(queryset=None)
    assert field.to_python('5') == [5]


def test__model_multiple_choice_text_field__to_python__multiple():
    field = ModelMultipleChoiceTextField(queryset=None)
    assert field.to_python('1,2,3000,9999999999') == [1, 2, 3000, 9999999999]


def test__model_multiple_choice_text_field__prepare_value__empty():
    field = ModelMultipleChoiceTextField(queryset=None)
    assert field.prepare_value([]) == ''


def test__model_multiple_choice_text_field__prepare_value__single():
    field = ModelMultipleChoiceTextField(queryset=None)
    assert field.prepare_value([17]) == '17'


def test__model_multiple_choice_text_field__prepare_value__multiple():
    field = ModelMultipleChoiceTextField(queryset=None)
    assert field.prepare_value([3, 8, 99999999]) == '3,8,99999999'


def test__model_multiple_choice_text_field__validate__empty_but_required():
    field = ModelMultipleChoiceTextField(queryset=None, required=True)
    with pytest.raises(exceptions.ValidationError) as exc:
        field.validate([])
    assert exc.value.code == 'required'


def test__model_multiple_choice_text_field__validate__empty_not_required():
    field = ModelMultipleChoiceTextField(queryset=None, required=False)
    # no exception thrown:
    field.validate([])


def test__model_multiple_choice_text_field__validate__single_valid():
    field = ModelMultipleChoiceTextField(queryset=None, required=False)
    # no exception thrown:
    field.validate([1])


def test__model_multiple_choice_text_field__validate__single_invalid():
    field = ModelMultipleChoiceTextField(queryset=None, required=False)
    with pytest.raises(exceptions.ValidationError) as exc:
        field.validate(1)
    assert exc.value.code == 'list'


@pytest.fixture
def queryset():
    Article(name='A', price=1.1).save()
    Article(name='B', price=2.2).save()
    return Article.objects.all()


@pytest.mark.django_db
def test__model_multiple_choice_text_field__clean__empty_not_required(queryset):
    field = ModelMultipleChoiceTextField(queryset=queryset, required=False)
    cleaned_data = field.clean('')
    assert len(cleaned_data) == 0


@pytest.mark.django_db
def test__model_multiple_choice_text_field__clean__empty_but_required(queryset):
    field = ModelMultipleChoiceTextField(queryset=queryset, required=True)
    with pytest.raises(exceptions.ValidationError) as exc:
        field.clean('')
    assert exc.value.code == 'required'


@pytest.mark.django_db
def test__model_multiple_choice_text_field__clean__multiple_with_unknown(queryset):
    field = ModelMultipleChoiceTextField(queryset=queryset)
    with pytest.raises(exceptions.ValidationError) as exc:
        field.clean('1,2,42')
    assert exc.value.code == 'invalid_choice'


@pytest.mark.django_db
def test__model_multiple_choice_text_field__clean__single_valid(queryset):
    field = ModelMultipleChoiceTextField(queryset=queryset)
    cleaned_data = list(field.clean('1'))
    assert len(cleaned_data) == 1
    assert cleaned_data[0].name == 'A'


@pytest.mark.django_db
def test__model_multiple_choice_text_field__clean__multiple_valid(queryset):
    field = ModelMultipleChoiceTextField(queryset=queryset)
    cleaned_data = list(field.clean(' 1 , 2 '))
    assert len(cleaned_data) == 2
    assert cleaned_data[0].name == 'A'
    assert cleaned_data[1].name == 'B'
