import genanki
import random
import tempfile
import os

def export_to_anki(flashcards, deck_name="Study Engine Deck"):
    """
    Exports a list of flashcards (db.Flashcard objects) to an Anki .apkg file.
    """
    model_id = random.randrange(1 << 30, 1 << 31)
    deck_id = random.randrange(1 << 30, 1 << 31)
    
    my_model = genanki.Model(
      model_id,
      'Study Engine Model',
      fields=[
        {'name': 'Question'},
        {'name': 'Answer'},
      ],
      templates=[
        {
          'name': 'Card 1',
          'qfmt': '{{Question}}',
          'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}',
        },
      ])
      
    my_deck = genanki.Deck(deck_id, deck_name)
    
    for fc in flashcards:
        # Convert LaTeX format from $..$ to \(..\) for Anki if needed, but Anki supports mathjax
        note = genanki.Note(
            model=my_model,
            fields=[fc.front, fc.back]
        )
        my_deck.add_note(note)
        
    temp_dir = tempfile.gettempdir()
    output_path = os.path.join(temp_dir, f"{deck_name.replace(' ', '_')}.apkg")
    
    genanki.Package(my_deck).write_to_file(output_path)
    return output_path

def export_markdown_summary(summary_text, title="Study Summary"):
    """
    Exports a summary to a Markdown file suitable for Obsidian/Notion.
    """
    md = f"# {title}\n\n"
    md += "*Exported from Academic Research & Study Engine*\n\n"
    md += summary_text
    
    temp_dir = tempfile.gettempdir()
    output_path = os.path.join(temp_dir, f"{title.replace(' ', '_')}.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md)
        
    return output_path
