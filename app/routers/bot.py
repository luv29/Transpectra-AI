from langchain_core.messages import HumanMessage, SystemMessage
from app.schemas import BotSchema
from fastapi import APIRouter
from app.bot import get_bot 
import json

router = APIRouter()

@router.post('/bot')
async def bot(query: BotSchema):
    conn = None

    try:
        bot, conn = await get_bot()

        config = {"configurable": {"thread_id": query.chat_id}}
        messages = [SystemMessage(content=f"""
            You are a chatbot for transpectra, a warehouse and inventory management platform that revolutionalizes logistics. You need to answer the queries of the warehouse managar, regarding the warehouse, tell him the amount of stock that he might require, tell him the best routes to ship cargos, tell him the resources that he might require in a day and answer all the basic doubts related to logistics and warehouse management.
                                  
            You are very creative when it comes to displaying outputs, so showcase your expert markdown skills and give visually stunning outputs.

            Your answer should short, clear and should solve the query of the user.

            Your tone must be polite and helpful. The user should be satisfied by your answer. You can ask the user follow up questions, to make your response evenn better?

            You may use the tools that you have access to, only when required.
            Give a beautiful Response, you may use markdown for your response. But provide a appealing output by which the user gets impressed.
                                  
            Give as fancy and creative output as possible. Make full use of markdown, the output should look very very good. Keep in mind. Make use of emojis, tables, different colors and any other thing if you can, the output should be visually stunning.""", role="system"),
            HumanMessage(content=query.prompt, role="user")]
        output = await bot.ainvoke({"messages": messages}, config)
        
        return {
            "reply": output['messages'][-1].content
        }

    except Exception as e:
        # print(f"Error: {e}")
        
        import traceback
        print("Error:", e)
        traceback.print_exc()
    finally:
        if conn:  
            await conn.close()
