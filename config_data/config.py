from dataclasses import dataclass
from environs import Env

@dataclass
class Tg_bot:
    token: str
    admin_ids: list[int]
    dsn: str
    deletion_psw: str

@dataclass
class Config:
    tg_bot: Tg_bot


def load_config(path: str | None = None) -> Config:

    env: Env = Env()
    env.read_env()

    return Config(
        tg_bot=Tg_bot(
            token=env('BOT_TOKEN'),
            admin_ids=list(map(int, env.list('ADMIN_ID'))),
            dsn=env('DSN'),
            deletion_psw=env('deletion_psw')
        )
    )
