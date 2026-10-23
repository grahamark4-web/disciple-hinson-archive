"""Refresh data, topic tags and platform episode links before publishing a new version."""
import subprocess,sys,pathlib,json
import platform_links
root=pathlib.Path(__file__).parent
for cmd in [[sys.executable,'build_catalog.py'],['node','enrich_catalog.cjs'],[sys.executable,'build_topics.py']]:subprocess.run(cmd,cwd=root,check=True)
platform_links.update_links(json.loads((root/'dist/episodes.json').read_text())['sermons'],root/'dist')
subprocess.run(['node','test_catalog.cjs'],cwd=root,check=True)

subprocess.run(['node','test_subjects.cjs'],cwd=root,check=True)
