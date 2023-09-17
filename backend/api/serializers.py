from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password'
        )
        extra_kwargs = {
            'id': {'read_only': True},
            'password': {'write_only': True},
        }


"""
class SignUpSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=254)
    username = serializers.CharField(
        max_length=150,
        validators=[
            UnicodeUsernameValidator(),
        ]
    )

    class Meta:
        model = User
        fields = ('email', 'username')

    def validate(self, data):
        username = data['username']
        email = data['email']
        users = User.objects.filter(Q(username=username) | Q(email=email))
        only_username_exists = (
            users.filter(username=username).exclude(email=email).exists()
        )
        only_email_exists = (
            users.filter(email=email).exclude(username=username).exists()
        )
        if only_username_exists:
            raise ValidationError(
                {'email': f'{username} уже зарегистрирован с другой почтой.'}
            )
        if only_email_exists:
            raise ValidationError(
                {'email': 'Данный адрес электронной почты уже используется.'}
            )
        return data

    def validate_username(self, value):
        if value == 'me':
            raise ValidationError(
                {'username': 'Запрещено использовать имя "me".'}
            )
        return value


class RecieveTokenSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=150,
        validators=[UnicodeUsernameValidator()],
    )
    confirmation_code = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150,
        validators=[UnicodeUsernameValidator()],
    )
    email = serializers.EmailField(
        max_length=254,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    bio = serializers.CharField(required=False)
    role = serializers.ChoiceField(choices=User.Roles.choices, required=False)

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        lookup_field = 'username'
        extra_kwargs = {'url': {'lookup_field': 'username'}}

    def validate_username(self, value):
        if (
            self.context['request'].method == 'POST'
            and User.objects.filter(username=value).exists()
        ):
            raise serializers.ValidationError(
                {'username': 'Данное имя пользователя уже используется.'}
            )
        return value
"""
