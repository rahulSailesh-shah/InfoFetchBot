import autogen

class WebInfoAgent:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WebInfoAgent, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        config_list = autogen.config_list_from_json(
            "OAI_CONFIG_LIST",
            filter_dict={
                "model": ["gpt-4"],
            },
        )

        if not config_list:
            raise ValueError("No valid configurations found. Check your OAI_CONFIG_LIST file.")

        llm_config = {
            "timeout": 600,
            "cache_seed": 42,
            "config_list": config_list,
            "temperature": 0,
        }

        self.assistant = autogen.AssistantAgent(
            name="assistant",
            llm_config=llm_config,
        )

        self.user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=10,
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
            code_execution_config={
                "work_dir": "webAgentCode",
                "use_docker": True,
            },
            llm_config=llm_config,
            system_message="""Reply TERMINATE if the task has been solved at full satisfaction.
            Or, TERMINATE with reason why the task is not solved.
            If you plan to scrape any website Please provide the link of the website as well.
            When providing information, please include sources or references when possible.""",
        )

        print("WebInfoAgent initialized.")

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def initiate_chat(self, message):
        message = "Give me some information about: " +  message
        print("Initiating chat with WebInfoAgent. Message:", message)
        try:
            response = self.user_proxy.initiate_chat(
                self.assistant,
                message=message,
                silent=False
            )
            return response
        except Exception as e:
            print(f"An error occurred while initiating chat: {e}")
