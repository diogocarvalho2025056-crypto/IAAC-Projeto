from typing import Any

from crewai import BaseLLM

from transformers import AutoModelForCausalLM, AutoTokenizer
import torch


class QwenLocalLLM(BaseLLM):

    def __init__(
        self,
        model_name: str = "Qwen/Qwen2.5-1.5B-Instruct"
    ):

        super().__init__(
            model=model_name,
            temperature=0.2
        )

        self.model_name = model_name

        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name
        )

        self.modelo = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype="auto",
            device_map="auto"
        )


    def call(
        self,
        messages: str | list[dict[str, Any]],
        tools=None,
        callbacks=None,
        available_functions=None
    ) -> str:

        if isinstance(
            messages,
            str
        ):

            mensagens = [
                {
                    "role": "user",
                    "content": messages
                }
            ]

        else:

            mensagens = messages


        texto = self.tokenizer.apply_chat_template(
            mensagens,
            tokenize=False,
            add_generation_prompt=True
        )


        entradas = self.tokenizer(
            texto,
            return_tensors="pt"
        ).to(
            self.modelo.device
        )


        with torch.no_grad():

            saida = self.modelo.generate(
                **entradas,
                max_new_tokens=300,
                do_sample=False
            )


        novos_tokens = saida[
            0,
            entradas["input_ids"].shape[1]:
        ]


        resposta = self.tokenizer.decode(
            novos_tokens,
            skip_special_tokens=True
        )


        return resposta.strip()


    def supports_function_calling(
        self
    ) -> bool:

        return False


    def supports_stop_words(
        self
    ) -> bool:

        return False


    def get_context_window_size(
        self
    ) -> int:

        return 32768