---
name: discord-mentions
description: Use when told to message a person. Tag them with a mention.
---

# Discord mentions

When sterling asks me to say something to someone ("say X to chef", "tell Y ..."), the reply must mention that person with a real Discord mention, not just their name in plain text.

## Mention syntax
- User: `<@USER_ID>`
- Role: `<@&ROLE_ID>`. Do not use a role when the request names a person.

## Procedure
1. Find the user ID with discord search_members(guild_id, query). Do not guess an ID.
2. If there are several matches, or none, ask sterling which one.
3. Put the mention at the start of the message, then the requested content.

## Why
Plain-text names do not ping anyone, and a role mention tags the wrong thing.