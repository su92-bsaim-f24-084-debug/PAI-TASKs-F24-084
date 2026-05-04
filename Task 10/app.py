from flask import Flask, render_template, request, jsonify
from nltk.chat.util import Chat, reflections

# ─────────────────────────────────────────────
#  40+ Pairs about "Large Language Models"
#  Every pattern uses the regex | operator
# ─────────────────────────────────────────────
pairs = [
    # ── Greetings ──────────────────────────────
    [
        r'hi|hello|hey|howdy|greetings',
        [
            "Hello! I'm your LLM expert. Ask me anything about Large Language Models! 🤖",
            "Hey there! Ready to explore the world of Large Language Models?",
        ]
    ],
    [
        r'how are you|how r u|how do you do',
        [
            "I'm doing great, thanks for asking! Let's talk about LLMs!",
            "Feeling brilliant! Ready to discuss everything about Large Language Models.",
        ]
    ],
    [
        r'good morning|good evening|good afternoon|good night',
        [
            "Good to see you! Let's dive into the fascinating world of Large Language Models.",
        ]
    ],

    # ── What is an LLM ─────────────────────────
    [
        r'what is (a|an)? ?(llm|large language model)|define llm|explain llm',
        [
            "A Large Language Model (LLM) is a type of AI model trained on massive text corpora to understand and generate human-like text. Examples include GPT-4, Claude, Gemini, and LLaMA.",
            "LLMs are deep learning models — primarily based on the Transformer architecture — that learn statistical patterns in language from billions of text documents.",
        ]
    ],
    [
        r'how does (an? )?(llm|large language model) work|working of llm',
        [
            "LLMs work by predicting the next token (word/subword) in a sequence. They are pre-trained on huge datasets using self-supervised learning and then fine-tuned for specific tasks.",
        ]
    ],

    # ── Transformer Architecture ────────────────
    [
        r'what is (a )?transformer|transformer architecture|transformer model',
        [
            "The Transformer is a neural network architecture introduced in the paper 'Attention Is All You Need' (2017). It uses self-attention mechanisms to process sequences in parallel, making it highly efficient for NLP tasks.",
        ]
    ],
    [
        r'what is (self-?attention|attention mechanism)|explain attention',
        [
            "Self-attention allows a model to weigh the importance of each word relative to all other words in a sentence simultaneously. It helps the model understand context and long-range dependencies.",
        ]
    ],
    [
        r'what are (encoder|decoder|encoder-decoder)|explain encoder decoder',
        [
            "In Transformers: the Encoder reads the input and creates a contextual representation; the Decoder generates output tokens one by one using those representations. GPT uses decoder-only; BERT uses encoder-only; T5 uses both.",
        ]
    ],

    # ── Training ───────────────────────────────
    [
        r'how (are|is) (llm|large language model)s? trained|llm training process',
        [
            "LLMs are trained in stages:\n1. Pre-training on large corpora via next-token prediction.\n2. Supervised Fine-Tuning (SFT) on curated datasets.\n3. RLHF (Reinforcement Learning from Human Feedback) to align with human preferences.",
        ]
    ],
    [
        r'what is pre-?training|explain pre-?training',
        [
            "Pre-training is the initial phase where an LLM learns general language understanding by predicting masked or next tokens on billions of documents. It is computationally expensive and typically done once.",
        ]
    ],
    [
        r'what is fine-?tuning|explain fine-?tuning',
        [
            "Fine-tuning adapts a pre-trained LLM to a specific task or domain using a smaller, labelled dataset. It is much cheaper than pre-training and allows specialization.",
        ]
    ],
    [
        r'what is rlhf|reinforcement learning from human feedback',
        [
            "RLHF (Reinforcement Learning from Human Feedback) is a technique where humans rank model outputs, and a reward model is trained on those rankings. The LLM is then fine-tuned via RL to maximize the reward, aligning the model with human intent.",
        ]
    ],

    # ── Popular Models ─────────────────────────
    [
        r'what is gpt|explain gpt|gpt model',
        [
            "GPT (Generative Pre-trained Transformer) is a family of decoder-only LLMs developed by OpenAI. GPT-4 is currently one of the most capable publicly available models, used in ChatGPT.",
        ]
    ],
    [
        r'what is bert|explain bert',
        [
            "BERT (Bidirectional Encoder Representations from Transformers) is an encoder-only model by Google. It reads text bidirectionally and excels at understanding tasks like classification, NER, and Q&A.",
        ]
    ],
    [
        r'what is claude|who made claude',
        [
            "Claude is an LLM family developed by Anthropic, designed with a focus on safety and helpfulness. I'm actually powered by Claude! 😊",
        ]
    ],
    [
        r'what is gemini|google gemini|explain gemini',
        [
            "Gemini is Google DeepMind's family of multimodal LLMs. It can process text, images, audio, and video, and powers many Google products.",
        ]
    ],
    [
        r'what is llama|meta llama|explain llama',
        [
            "LLaMA (Large Language Model Meta AI) is Meta's open-source LLM series. LLaMA 3 is highly competitive and can be run locally, enabling privacy-preserving AI applications.",
        ]
    ],
    [
        r'what is mistral|explain mistral',
        [
            "Mistral is a family of open-weight LLMs developed by Mistral AI (France). They are known for being efficient and high-performing relative to their size.",
        ]
    ],

    # ── Tokens & Parameters ────────────────────
    [
        r'what (is|are) tokens?|explain token(ization)?',
        [
            "Tokens are the basic units LLMs process. A token can be a word, part of a word, or a character. For example, 'unhappy' might be split into 'un' and 'happy'. Models have a context window measured in tokens.",
        ]
    ],
    [
        r'what (is|are) parameters?|how many parameters|model parameters',
        [
            "Parameters are the learnable weights inside an LLM. More parameters generally means more capacity to learn complex patterns. GPT-4 is estimated to have ~1.7 trillion parameters across its mixture of experts.",
        ]
    ],
    [
        r'what is context (window|length)|context window size',
        [
            "The context window is the maximum number of tokens an LLM can consider at once (input + output). GPT-4 supports up to 128K tokens; Gemini 1.5 Pro supports up to 1 million tokens.",
        ]
    ],

    # ── Prompting Techniques ───────────────────
    [
        r'what is prompt engineering|explain prompt engineering',
        [
            "Prompt engineering is the practice of crafting effective inputs (prompts) to get the best outputs from an LLM. It includes techniques like zero-shot, few-shot, chain-of-thought, and role prompting.",
        ]
    ],
    [
        r'what is (zero-shot|zero shot) (prompting)?|zero-shot learning',
        [
            "Zero-shot prompting asks the model to perform a task without any examples. E.g., 'Translate this sentence to French: Hello!' — no French examples are given.",
        ]
    ],
    [
        r'what is (few-shot|few shot) (prompting)?|few-shot learning',
        [
            "Few-shot prompting provides a small number of input-output examples in the prompt before the actual query, helping the model understand the desired format or task.",
        ]
    ],
    [
        r'what is chain.of.thought|cot prompting|explain cot',
        [
            "Chain-of-Thought (CoT) prompting encourages the model to reason step-by-step before giving a final answer. This significantly improves performance on math, logic, and complex reasoning tasks.",
        ]
    ],
    [
        r'what is rag|retrieval augmented generation|explain rag',
        [
            "RAG (Retrieval-Augmented Generation) combines an LLM with a retrieval system (e.g., a vector database). Relevant documents are fetched and inserted into the prompt, reducing hallucinations and enabling up-to-date knowledge.",
        ]
    ],

    # ── Hallucinations & Safety ────────────────
    [
        r'what (is|are) hallucination(s)?|llm hallucination|why does (the )?(llm|bot|ai) lie',
        [
            "Hallucinations occur when an LLM generates plausible-sounding but factually incorrect information. They happen because the model predicts statistically likely tokens, not verified facts. RAG and fact-checking pipelines help mitigate this.",
        ]
    ],
    [
        r'what is ai safety|llm safety|how (is|are) llm(s)? made safe',
        [
            "LLM safety involves techniques like RLHF, Constitutional AI (Anthropic), and content filters to prevent harmful, biased, or misleading outputs. Organizations like Anthropic and OpenAI have dedicated safety teams.",
        ]
    ],
    [
        r'what is bias in (llm|ai)|ai bias|llm bias',
        [
            "Bias in LLMs refers to systematic errors or prejudices in model outputs reflecting biases in training data (e.g., gender, racial, cultural biases). Debiasing techniques include curated datasets, RLHF, and post-hoc filtering.",
        ]
    ],

    # ── Applications ───────────────────────────
    [
        r'what can (llm|large language model)s? do|llm applications|uses of llm',
        [
            "LLMs can: answer questions, write code, summarize documents, translate languages, generate creative content, power chatbots, analyze sentiment, extract information, and much more!",
        ]
    ],
    [
        r'can llm(s)? write code|llm coding|code generation (with|using) llm',
        [
            "Yes! LLMs like GPT-4, Claude, and CodeLlama can write, debug, and explain code in many programming languages. Tools like GitHub Copilot are powered by LLMs.",
        ]
    ],
    [
        r'can llm(s)? (understand|process) images?|multimodal llm|vision llm',
        [
            "Multimodal LLMs (like GPT-4V, Gemini, and Claude) can process both text and images. They can describe images, answer visual questions, and analyze charts or diagrams.",
        ]
    ],

    # ── Technical Details ──────────────────────
    [
        r'what is embedding(s)?|word embedding|vector embedding',
        [
            "Embeddings are dense numerical vector representations of tokens/words. Similar words have similar embeddings (close in vector space). LLMs use learned embeddings as input representations.",
        ]
    ],
    [
        r'what is (a )?vector (database|store|db)|explain vector database',
        [
            "A vector database stores high-dimensional embeddings and supports fast similarity search (e.g., cosine similarity). They are essential for RAG pipelines. Popular ones: Pinecone, Weaviate, Chroma, FAISS.",
        ]
    ],
    [
        r'what is temperature (in llm)?|llm temperature|sampling temperature',
        [
            "Temperature is a parameter (0–2) that controls LLM output randomness. Low temperature (e.g., 0.1) gives focused, deterministic answers. High temperature (e.g., 1.5) gives diverse, creative but less coherent outputs.",
        ]
    ],
    [
        r'what is top.p|nucleus sampling|top.k sampling',
        [
            "Top-p (nucleus) sampling selects from the smallest set of tokens whose cumulative probability exceeds p. Top-k restricts sampling to the k most likely tokens. Both control output diversity alongside temperature.",
        ]
    ],
    [
        r'what is (a )?mixture of experts|moe|explain moe',
        [
            "Mixture of Experts (MoE) is an architecture where only a subset of model 'experts' (sub-networks) are activated for each token. This allows huge parameter counts without proportionally huge compute costs. GPT-4 and Mixtral use MoE.",
        ]
    ],

    # ── Compute & Resources ────────────────────
    [
        r'how much compute|how expensive (is|are) llm|llm training cost',
        [
            "Training a frontier LLM can cost tens of millions to hundreds of millions of dollars in compute. GPT-4 is estimated to have cost over $100 million to train. Inference is much cheaper but still significant at scale.",
        ]
    ],
    [
        r'what gpu(s)? (are used|do you need)|hardware for llm|nvidia gpu llm',
        [
            "LLMs are typically trained on clusters of NVIDIA H100 or A100 GPUs. For local inference, consumer GPUs like RTX 4090 can run smaller models (7B–13B parameters) with quantization.",
        ]
    ],
    [
        r'what is quantization|llm quantization|4.bit quantization',
        [
            "Quantization reduces the precision of model weights (e.g., from 32-bit floats to 4-bit integers), dramatically shrinking model size and inference cost with minimal quality loss. Tools like GPTQ and bitsandbytes are popular.",
        ]
    ],

    # ── Future & Ethics ────────────────────────
    [
        r'future of llm|what.s next for llm|llm future',
        [
            "The future of LLMs includes: longer context windows, better reasoning, multimodality (text+image+audio+video), more efficient architectures, and deeper integration into software and robotics.",
        ]
    ],
    [
        r'(are|is) llm(s)? dangerous|llm risks|ai risks',
        [
            "LLMs carry risks: misinformation, deepfakes, job displacement, misuse by bad actors, and existential concerns about AGI. Responsible AI development, regulation, and alignment research are critical countermeasures.",
        ]
    ],
    [
        r'what is agi|artificial general intelligence|agi vs llm',
        [
            "AGI (Artificial General Intelligence) refers to AI that can perform any intellectual task a human can. Current LLMs are not AGI — they are powerful but narrow tools. AGI remains an open research goal.",
        ]
    ],

    # ── Farewell ───────────────────────────────
    [
        r'exit|bye|goodbye|quit|see you|take care',
        [
            "Goodbye! It was great chatting about Large Language Models. Keep exploring AI! 👋",
        ]
    ],
    [
        r'thank(s| you)|thx|thanks a lot',
        [
            "You're welcome! Feel free to ask me anything about LLMs anytime. 😊",
            "Happy to help! AI is a fascinating field — keep learning!",
        ]
    ],
    [
        r'(.*)',
        [
            "Interesting question! I specialize in Large Language Models. Could you ask something related to LLMs, transformers, or AI?",
            "I'm not sure I understand. Try asking about LLMs, GPT, BERT, training, prompting, or AI safety!",
        ]
    ],
]

# ─────────────────────────────────────────────
#  Flask App Setup
# ─────────────────────────────────────────────
app = Flask(__name__)
chatbot = Chat(pairs, reflections)

EXIT_TRIGGERS = {'exit', 'bye', 'goodbye', 'quit', 'see you', 'take care'}


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/get', methods=['GET'])
def get_bot_response():
    user_text = request.args.get('msg', '').strip()
    if not user_text:
        return jsonify({'response': 'Please type a message!', 'terminate': False})

    response = chatbot.respond(user_text)
    if response is None:
        response = "I'm not sure about that. Try asking about LLMs, GPT, BERT, or AI safety!"

    # Detect termination
    terminate = any(trigger in user_text.lower() for trigger in EXIT_TRIGGERS)

    return jsonify({'response': response, 'terminate': terminate})


if __name__ == '__main__':
    app.run(debug=True)
