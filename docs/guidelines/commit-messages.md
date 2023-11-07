# Commit Guidelines

### TL;DR
- Link every commit to an issue or branch.
- Commit often but only completed changes.
- Verify changes before committing.
- Write concise commit messages in the imperative present tense.

  ---

1. **Relate every commit to a specific change**: Each commit should correspond to an issue or branch. Thus, if there are two different problems to fixed, each of them should have a commit for themselves. This way, smaller and specific changes are more easy to follow and make the progress easier to track.
2. **Commit often**: It’s better to commit small and frequent changes, than pilling up more tasks and committing them rarely. But always remember to relate those small commits to issues and branches as well!
3. **Commit only completed changes**: Commits should always contain completed tasks to track an incremental progress of the product and know wich functionality is already implemented. Commits should leave no functionality broken.
4. **Write meaningful commit messages**:
   1. `git commit -m <title> -m <description>`
   2.  The title should not exceed 50 characters and the description should not be longer than 72 characters.
   3. Keep it short and stick to the main idea.
   4. Use the imperative of the present tense e.g. `fix change`
   5. The message should answer the following questions: “What was the reason for the change?” and “How was it implemented?”.
5. **Check changes before committing**: Make sure to carefully test or check the implemented changes before making a commit. This avoid complications and future work.
6. **Be concise** and attempt to avoid using extraneous words and phrases.
