from typing import Final

MODELS :Final[list[str]] = [
    #                             Input     Cached input    Output
    "gpt-5-nano",	            # $0.05	    $0.005	        $0.40
    "gpt-5-mini",	            # $0.25	    $0.025	        $2.00
    "gpt-5-codex",	            # $1.25	    $0.125	        $10.00

    "gpt-5.1",	                # $1.25	    $0.125	        $10.00
    "gpt-5.1-chat-latest",	    # $1.25	    $0.125	        $10.00
    "gpt-5.1-codex-max",	    # $1.25	    $0.125	        $10.00
    "gpt-5.1-codex",	        # $1.25	    $0.125	        $10.00

    "gpt-5-chat-latest",	    # $1.25	    $0.125	        $10.00

    "gpt-5.2",	                # $1.75	    $0.175	        $14.00
    "gpt-5.2-chat-latest",	    # $1.75	    $0.175	        $14.00
    "gpt-5.2-codex",	        # $1.75	    $0.175	        $14.00

    "gpt-5-pro",	            # $15.00    	-	        $120.00
    "gpt-5.2-pro",	            # $21.00    	-	        $168.00
]

DEFAULT_MODEL :Final[str] = "gpt-5-nano"
