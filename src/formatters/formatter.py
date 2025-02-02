def format_important_points(points):
    # Define a list of emojis to use for bullet points
    emojis = ["📝"]
    
    # Start with a header
    message = "```\n📋 Important Points\n\n"
    
    # Add each point with an emoji
    for i, point in enumerate(points):
        emoji = emojis[i % len(emojis)]  # Cycle through emojis if there are more points than emojis
        message += f"{emoji} {point}\n"
    
    # Add a footer
    message += "\n📌 Stay organized and keep these points in mind!\n```"
    
    return message

def format_tasks(tasks):
    if(len(tasks) == 0):
        return "```No Tasks Discussed in conversation```"
    # Define emojis for priorities
    priority_emojis = {
        "High": "🔴",  # Red circle for high priority
        "Medium": "🟡",  # Yellow circle for medium priority
        "Low": "🟢",  # Green circle for low priority
    }
    
    # Start with a header
    message = "```diff\n📋 Tasks Overview\n\n"
    
    # Add each task with its priority emoji
    for task in tasks:
        task_name = task.get("task", "Unnamed Task")
        priority = task.get("priority", "Medium")  # Default to Medium if priority is missing
        emoji = priority_emojis.get(priority, "🟡")  # Default to Medium emoji if priority is invalid
        message += f"{emoji} {priority} Priority: {task_name}\n"
    
    # Add a footer
    message += "\n📌 Stay focused and prioritize your tasks!\n```"
    
    return message

def format_summary(summary):
    # Start with a header
    message = "```yaml\n📄 Conversation Summary\n\n"
    
    # Add the summary text
    message += f"✨ Summary: {summary}\n\n"
    
    # Add a footer
    message += "📌 Keep this summary handy for reference!\n```"
    
    return message