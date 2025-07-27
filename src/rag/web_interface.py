# New minimal Flask web interface – rewritten from scratch
from flask import Flask, request, jsonify, render_template_string
from config.settings import Config
from src.rag.rag_system import ASURAGSystem


def create_app(config: Config, rag_system: ASURAGSystem) -> Flask:
    """Return a minimal, self-contained Flask app that serves a very small
    single-page interface for querying the RAG system.  It purposely avoids
    any complex string concatenation pitfalls and depends only on the /stats
    and /query backend routes.  No external assets are required – everything
    (HTML, CSS, JS) is inlined.
    """

    page = render_template_string(
        """<!DOCTYPE html>
<html lang=\"en\">
<head>
<meta charset=\"utf-8\"/>
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"/>
<title>ASU RAG</title>
<style>
 html,body{margin:0;padding:0;font-family:system-ui,sans-serif;background:#6b73ff;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);min-height:100vh;display:flex;align-items:center;justify-content:center;color:#2c3e50}
 #box{background:#fff;width:100%;max-width:800px;border-radius:16px;padding:32px;box-shadow:0 6px 32px rgba(0,0,0,.15)}
 h1{margin:0 0 12px;text-align:center}
 #stats{font-weight:600;text-align:center;margin:0 0 24px}
 .row{display:flex;gap:8px}
 input{flex:1;padding:12px;border:2px solid #e9ecef;border-radius:8px;font-size:1rem}
 input:focus{outline:none;border-color:#667eea}
 button{padding:12px 20px;border:none;border-radius:8px;background:#667eea;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:#fff;font-weight:600;font-size:1rem;cursor:pointer}
 #result{margin-top:24px;line-height:1.6}
 .src{margin-top:12px;padding:12px;background:#fafafa;border-left:4px solid #667eea;border-radius:6px;font-size:.9rem}
 .src a{color:#667eea;word-break:break-all;font-size:.8rem}
 .loading{color:#667eea;font-weight:600;text-align:center}
</style>
</head>
<body>
<div id=\"box\">
 <h1>🏛️ ASU RAG System</h1>
 <div id=\"stats\">📊 Loading stats…</div>
 <div class=\"row\">
  <input id=\"q\" placeholder=\"Ask something about ASU…\"/>
  <button id=\"btn\">🔍 Ask</button>
 </div>
 <div id=\"result\"></div>
</div>
<script>
 const $ = id=>document.getElementById(id);
 const ajax = (url, opts={})=>fetch(url,opts).then(r=>{if(!r.ok)throw new Error(r.status);return r.json()});
 async function loadStats(){try{const s=await ajax('/stats');$('stats').textContent=`📊 ${s.vector_store.total_documents} docs | ${s.vector_store.collection_name}`;}catch(e){$('stats').textContent='⚠️ Stats unavailable';}}
 async function ask(){const q=$('q').value.trim();if(!q)return alert('Enter a question');$('result').innerHTML='<p class="loading">⏳ Thinking…</p>';try{const d=await ajax('/query',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:q})});let html=`<h2>Answer</h2><p>${d.answer.replaceAll('\\n','<br>')}</p>`;if(d.sources?.length){html+='<h3>Sources</h3>';d.sources.forEach(s=>{html+=`<div class='src'><strong>${s.title||'No title'}</strong><br><a href='${s.url}' target='_blank'>${s.url}</a><br>Score: ${(s.score*100).toFixed(1)}%<p>${s.content_preview}</p></div>`})} $('result').innerHTML=html;}catch(e){$('result').innerHTML=`<p class='loading'>❌ ${e.message}</p>`}}
 document.addEventListener('DOMContentLoaded',()=>{loadStats();$('btn').onclick=ask;$('q').addEventListener('keypress',e=>{if(e.key==='Enter')ask()})});
</script>
</body>
</html>""")

    app = Flask(__name__)

    @app.route('/')
    def home():
        return page

    @app.route('/stats')
    def stats():
        return jsonify(rag_system.get_stats())

    @app.route('/query', methods=['POST'])
    def query():
        body = request.get_json(silent=True) or {}
        question = (body.get('question') or '').strip()
        if not question:
            return jsonify({'error': 'question missing'}), 400
        return jsonify(rag_system.query(question, top_k=5))

    return app
