"""Seek mobs and kill them."""
import asyncio
import logging
import time
from typing import Callable

from telethon import events, types

from epsilion_wars_mmorpg_automation.actions import (
    complete_battle,
    healing,
    ping,
    search_enemy,
    select_attack_direction,
    select_combo,
    select_defence_direction,
)
from epsilion_wars_mmorpg_automation.message_parsers import checks, parsers
from epsilion_wars_mmorpg_automation.settings import app_settings
from epsilion_wars_mmorpg_automation.telegram_client import client


async def main(execution_limit_minutes: int | None = None) -> None:
    """Grinding runner."""
    local_settings = {
        'execution_limit_minutes': execution_limit_minutes or 'infinite',
        'minimum_hp_level_for_grinding': app_settings.minimum_hp_level_for_grinding,
        'auto_healing_enabled': app_settings.auto_healing_enabled,
    }
    logging.info(f'start grinding ({local_settings=})')
    logging.info('move u character to hunting location first')

    me = await client.get_me()
    logging.info('auth as %s', me.username)

    game_user: types.InputPeerUser = await client.get_input_entity(app_settings.game_username)
    logging.debug('game user is %s', game_user)

    client.add_event_handler(
        callback=_grind_handler,
        event=events.NewMessage(
            incoming=True,
            from_users=(game_user.user_id,),
        ),
    )

    await ping(game_user.user_id)

    await _run_wait_loop(execution_limit_minutes)
    logging.info('end grinding by time left')


async def _run_wait_loop(execution_limit_minutes: int | None) -> None:
    start_time = time.time()
    execution_time = float(0)
    time_limit = (execution_limit_minutes or 0) * 60

    while not time_limit or execution_time < time_limit:
        await asyncio.sleep(10)
        logging.debug('next iteration')
        execution_time = time.time() - start_time


async def _grind_handler(event: events.NewMessage.Event) -> None:
    message_content = parsers.strip_message(event.message.message)
    logging.info('handle event %s', message_content[:app_settings.message_log_limit])

    await event.message.mark_read()

    select_callback = _select_action_by_event(event)

    await select_callback(event)


def _select_action_by_event(event: events.NewMessage.Event) -> Callable:
    mapping = [
        (checks.is_selector_combo, select_combo),
        (checks.is_selector_attack_direction, select_attack_direction),
        (checks.is_selector_defence_direction, select_defence_direction),
        (checks.is_win_state, complete_battle),
        (checks.is_died_state, _end_game),
        (checks.is_hp_updated_message, ping),
        (checks.is_hunting_ready_message, _hunting_optional),
    ]

    for check_function, callback_function in mapping:
        if check_function(event):
            logging.debug('is %s event', check_function.__name__)
            return callback_function

    return _skip_event


async def _end_game(event: events.NewMessage.Event) -> None:
    raise RuntimeError('U died :RIP:')


async def _hunting_optional(event: events.NewMessage.Event) -> None:
    hp_level_percent = parsers.get_hp_level(
        message_content=parsers.strip_message(event.message.message),
    )
    logging.info('current HP level is %d%%', hp_level_percent)

    if hp_level_percent >= app_settings.minimum_hp_level_for_grinding:
        await search_enemy(event)
    elif app_settings.auto_healing_enabled:
        await healing(event)


async def _skip_event(event: events.NewMessage.Event) -> None:
    logging.debug('skip event')
