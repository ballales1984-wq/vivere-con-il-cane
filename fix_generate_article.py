import re

with open('generate_article_fixed.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Sostituzioni
content = content.replace('_generate_grok', '_generate_groq')
content = content.replace('Generate using Grok API (xAI)', 'Generate using Groq API')
content = content.replace('using Grok or OpenAI AI', 'using Groq AI')
content = content.replace('gsk_... your Groq API key', 'gsk_...')  # placeholder
content = content.replace('OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")', '')
content = content.replace('OPENAI_API_KEY', '# OPENAI_API_KEY removed')  # comment out any remaining

# Rimuovi blocco elif OPENAI_API_KEY
lines = content.split('\n')
out = []
skip = False
indent_level = None
for line in lines:
    strip = line.lstrip()
    if 'elif OPENAI_API_KEY' in line:
        skip = True
        indent_level = len(line) - len(strip)
        continue
    if skip:
        current_indent = len(line) - len(strip)
        if strip and current_indent <= indent_level:
            skip = False
            out.append(line)
        continue
    out.append(line)

content = '\n'.join(out)

# Rimuovi funzione _generate_openai
content = re.sub(r'\ndef _generate_openai\(self, topic\):.*?(?=\n    def |\Z)', '', content, flags=re.DOTALL)

with open('blog/management/commands/generate_article.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('File aggiornato con successo')
