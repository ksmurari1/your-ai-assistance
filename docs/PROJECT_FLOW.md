# Project Flow — Mermaid Diagrams

These diagrams document the current frozen code flow. They can be rendered by GitHub in Markdown files that support Mermaid.

## End-to-end application flow

```mermaid
flowchart TD
    START([User opens app]) --> PAGE{Choose workspace page}

    PAGE -->|Task Playground| INPUT[Enter task]
    INPUT --> FORMAT[Select output format]
    FORMAT --> PROMPT[Use active RTCFR system prompt]
    PROMPT --> EMPTY{Task empty?}
    EMPTY -->|Yes| WARN[Show input warning]
    EMPTY -->|No| KEY{API key configured?}
    KEY -->|No| KEYERR[Show configuration error]
    KEY -->|Yes| MOD[Moderation check]

    MOD --> MODOK{Allowed?}
    MODOK -->|No| BLOCK[Show blocked result]
    MODOK -->|Moderation error| FAIL[Stop and show error]
    MODOK -->|Yes| CALLS{Action}
    CALLS -->|Generate| ONE[One generation call]
    CALLS -->|Compare| TWO[Two generation calls]

    ONE --> BUILD[Build SystemMessage + HumanMessage]
    TWO --> BUILD
    BUILD --> MODEL[LangChain ChatOpenAI]
    MODEL --> VALIDATE[Validate selected output format]
    VALIDATE --> DISPLAY[Display response]
    DISPLAY --> DOWNLOAD[Optional text download]

    PAGE -->|Guardrail Lab| LAB[Select sample or custom text]
    LAB --> CHECK[Call moderation only]
    CHECK --> LABRESULT[Show allow/block + details]

    PAGE -->|RTCFR Prompt| EDIT[Edit multi-line RTCFR prompt]
    EDIT --> APPLY{Apply or reset?}
    APPLY -->|Apply| SESSION[Update active session prompt]
    APPLY -->|Reset| DEFAULT[Restore default prompt]

    PAGE -->|About| ABOUT[Show project capabilities]
```

## Generation-only flow

```mermaid
flowchart LR
    TASK[User task] --> HUMAN[HumanMessage]
    RTCFR[Active RTCFR prompt] --> SYSTEM[SystemMessage]
    HUMAN --> MESSAGES[LangChain messages]
    SYSTEM --> MESSAGES
    MESSAGES --> CHAT[ChatOpenAI]
    CHAT --> CONTENT[Extract response content]
    CONTENT --> VALIDATE[Format-specific validation]
    VALIDATE --> UI[Render in Streamlit]
```

## Guardrail-only flow

```mermaid
flowchart TD
    INPUT[Task + active RTCFR prompt] --> MOD[OpenAI Moderation API]
    MOD --> RESULT[Inspect flagged state and categories]
    RESULT --> DECISION{Configured category flagged?}
    DECISION -->|Yes| BLOCK[Block; skip generation]
    DECISION -->|No| ALLOW[Allow request to proceed]
    MOD -->|API error| ERROR[Fail closed; show error]
```

## Original assignment script

`breakfast.py` is kept as a standalone path for the original assignment. It should not be confused with the generalized Streamlit path above.

```mermaid
flowchart TD
    START([Run breakfast.py]) --> ENV[Read OPENAI_API_KEY]
    ENV --> PROMPT[Build breakfast-specific prompt]
    PROMPT --> CHAT[Invoke LangChain ChatOpenAI]
    CHAT --> CONTENT[Read reply.content]
    CONTENT --> OUTPUT[Print breakfast ideas to terminal]
```
