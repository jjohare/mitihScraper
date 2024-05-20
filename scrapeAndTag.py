import os
import re
from scrapegraphai.graphs import SmartScraperGraph

def load_key(file_path):
    with open(file_path, 'r') as file:
        return file.read().strip()

def load_links(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file]

def load_topics(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file]

def save_to_markdown(text, file_path):
    with open(file_path, 'a') as file:
        file.write(text + '\n\n')

def create_prompt(url, topics):
    topics_str = ", ".join(topics)
    prompt = (
        f"Please create a short summary of the web page at the provided URL, unless it is a 404 or similar failure. "
        f"The response should follow these guidelines:\n\n"
        f"- Start the summary with a hyphen followed by a space ('- ').\n"
        f"- If bullet points are appropriate, use a tab followed by a hyphen and a space ('\\t- ') for each point, which is compliant with logseq markdown.\n"
        f"- Embed the web URL inline within the descriptive text, selecting a word sequence of high relevance to the summary.\n"
        f"- Check the provided list of topics and try to find the most relevant ones. If multiple relevant topics are found, include each of them inline within the summary, surrounded by double square brackets (e.g., [[topic1]], [[topic2]]).\n"
        f"- Each relevant topic should be tagged only once in the summary.\n"
        f"- Use UK English spelling throughout.\n"
        f"- If the web page is a 404 or otherwise inaccessible, do not return a summary.\n\n"
        f"Here are a few examples of the desired summary format:\n\n"
        f"Example 1:\n"
        f"- The [article](https://calpaterson.com/blockchain.html) discusses the limited and specific use-cases of [[blockchain]], arguing that "
        f"they are not a general-purpose technology. Blockchains are compared to databases, with the author suggesting that traditional, "
        f"centralised databases are faster, cheaper, and can handle larger data sets.\n\n"
        f"Example 2:\n"
        f"- This [blog post](https://example.com/ai-assistants) explores the advancements in [[Large language models]] and their potential impact on "
        f"various industries. The author highlights the benefits of AI-powered virtual assistants and discusses the challenges in developing safe and "
        f"ethical [[AI]] systems.\n\n"
        f"Example 3:\n"
        f"- The [research paper](https://example.org/metaverse-applications) delves into the potential applications of the [[Metaverse]] in fields such as "
        f"education, gaming, and social interaction. It examines the current state of [[Virtual Production]] technologies and discusses the challenges in "
        f"creating immersive and accessible virtual environments.\n\n"
        f"Example 4:\n"
        f"- This [news article](https://example.net/ai-regulation) reports on the proposed regulations for [[AI]] development and deployment. It covers the "
        f"key aspects of the regulations, including transparency, accountability, and ethical considerations. The article also discusses the potential "
        f"implications for businesses and the importance of striking a balance between innovation and [[Trust and Safety]].\n\n"
        f"Example 5:\n"
        f"- The [webinar](https://example.com/spatial-web) introduces the concept of the [[Spatial Web]] and its role in shaping the future of the internet. "
        f"The presenters explain how [[Spatial Computing]] technologies, such as [[Mixed reality]] and [[WebDev and Consumer Tooling]], enable new forms of "
        f"interaction and content creation. They also discuss the potential impact on various industries and the challenges in ensuring privacy and security "
        f"in the [[Spatial Web]].\n\n"
        f"List of topics to consider: {topics_str}\n\n"
        f"URL to summarize: {url}"
    )
    return prompt

def process_link(url, openai_key, topics):
    graph_config = {
        "llm": {
            "api_key": openai_key,
            "model": "gpt-3.5-turbo-0125",
        },
    }

    prompt = create_prompt(url, topics)

    smart_scraper_graph = SmartScraperGraph(
        prompt=prompt,
        source=url,
        config=graph_config
    )

    try:
        result = smart_scraper_graph.run()
        print("Result:", result)  # Debugging line to check the structure of result
        summary = result.get('summary', '').strip().replace('"', '')

        if not summary or '404' in summary:
            print(f"No summary found for URL: {url}")
            return None

        for topic in topics:
            if topic.lower() in summary.lower():
                summary = re.sub(r'(\b{}\b)'.format(re.escape(topic)), r'[[{}]]'.format(topic), summary, count=1, flags=re.IGNORECASE)

        return summary
    except Exception as e:
        print(f"Error processing {url}: {e}")
        return None

def main():
    openai_key = load_key('key.txt')
    links = load_links('links.txt')
    topics = load_topics('topics.txt')

    for link in links:
        summary = process_link(link, openai_key, topics)
        if summary:
            save_to_markdown(summary, 'markdown.md')

if __name__ == '__main__':
    main()
