# Creating a new feature

1. Copy the sample directory and give it a new suitable name.
2. Replace the command keyword, description and action ID.
3. Add the new directory as an import in `otto/__init__.py` (to register the feature).
4. Add functionality to the command and actions.

Note: An action file is only needed if you plan on using blocks to trigger a function.
