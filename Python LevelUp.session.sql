select
            game.id,
            game.title,
            game.maker,
            game.game_type_id,
            game.skill_level,
            game.num_of_players,
            game.gamer_id,
            user.id user_id,
            user.first_name || ' ' || user.last_name as full_name
            from levelupapi_game game
            join levelupapi_gamer gamer on gamer.id = game.gamer_id
            join auth_user user on gamer.user_id = user.id

select * from levelupapi_game