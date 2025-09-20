import typing as T
import re


MES = "Ошибка валидации входных данных"
USERNAME_RE = re.compile(r'^[A-Za-z0-9._-]{3,30}$')
EMAIL_RE = re.compile(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
URL_RE = re.compile(
    r'^(https?://)'
    r'([a-zA-Z0-9-]+\.)+'
    r'[a-zA-Z]{2,}'
    r'(/[^\s]*)?$'
)
FLAG_RE = re.compile(r'^(?!-{1,2})[\w.@+-]+$')


def sanitize_flag(value: T.Any):
    if not bool(FLAG_RE.match(value)):
        raise ValueError("Входные данные содержат недопустимые символы")


def clean_username(username: str) -> str:
    sanitize_flag(username)
    if not username:
        raise ValueError("Переданное значение не похоже на юзернейм")
    username = str(username)
    match = USERNAME_RE.fullmatch(username)
    if not match:
        raise ValueError("Переданное значение не похоже на юзернейм")
    return str(match[0])


def clean_email(email: str) -> str:
    sanitize_flag(email)
    if not email:
        raise ValueError("Переданное значение не похоже на эмейл")
    email = str(email)
    match = EMAIL_RE.fullmatch(email)
    if not match:
        raise ValueError("Переданное значение не похоже на эмейл")
    return str(match[0])


def is_url(url: str) -> bool:
    if not url:
        return False
    return bool(URL_RE.match(url))


def clean_file_line(line: str | bytes) -> str:
    if isinstance(line, bytes):
        line = line.decode('utf-8')
    
    return line.replace(r"\n", "").replace(r"\t", "").strip()


def clean_username_or_email(username_or_email: str) -> str:
    if not username_or_email:
        raise ValueError("Не передано значение")
    try:
        return clean_username(username_or_email)
    except ValueError:
        try:
            return clean_email(username_or_email)
        except ValueError as exc:
            raise ValueError("Переданное значение не похоже ни на эмелй ни на юзернейм") from exc


def extract_username_from_email(email: str) -> str:
    if not email:
        raise ValueError("Не передано значение")
    cleaned_email = clean_email(email)
    return cleaned_email.split("@")[0]
