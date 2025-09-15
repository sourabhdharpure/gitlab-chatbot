import streamlit as st
from datetime import datetime

class UIComponents:
    def __init__(self):
        pass

    def render_simple_chat(self, chatbot_manager, performance_monitor):
        chatbot = chatbot_manager.get_chatbot()
        
        # Initialize messages if not exists
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        if prompt := st.chat_input("Ask about GitLab..."):
            with st.chat_message("user"):
                st.write(prompt)
            
            with st.chat_message("assistant"):
                response_placeholder = st.empty()
                response_placeholder.write("Thinking...")
                
                try:
                    import time
                    start_time = time.time()
                    response, sources, token_info = chatbot.chat(prompt)
                    response_time = time.time() - start_time
                    
                    response_placeholder.write(response)
                    
                    performance_monitor.record_query(
                        query=prompt,
                        response_time=response_time,
                        cache_hit=False,
                        confidence_score=0.8,
                        error=None,
                        input_tokens=token_info.get('input_tokens', 0),
                        output_tokens=token_info.get('output_tokens', 0),
                        total_tokens=token_info.get('total_tokens', 0),
                        cost_usd=token_info.get('cost_usd', 0.0)
                    )
                    
                    st.session_state.messages.append({"role": "assistant", "content": response})
                
                except Exception as e:
                    response_placeholder.error(f"Error: {e}")

    def render_enhanced_chat(self, chatbot_manager, performance_monitor, cache_manager, smart_suggestions, transparency_guardrails):
        chatbot = chatbot_manager.get_chatbot()
        
        # Initialize messages if not exists
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        for i, message in enumerate(st.session_state.messages):
            with st.chat_message(message["role"]):
                st.write(message["content"])
                
                if message["role"] == "assistant" and ("sources" in message or "confidence" in message or "query" in message):
                    if st.button("More", key=f"more_{i}_{hash(message.get('content', ''))}"):
                        st.session_state[f"show_more_{i}"] = not st.session_state.get(f"show_more_{i}", False)
                        st.rerun()
                    
                    if st.session_state.get(f"show_more_{i}", False):
                        st.markdown("---")
                        
                        if message.get("confidence"):
                            transparency_guardrails.render_confidence_display(message["confidence"])
                        
                        with st.expander("Decision Trail", expanded=False):
                            transparency_guardrails.render_decision_trail(
                                message.get("query", ""), 
                                message["content"], 
                                message.get("sources", []), 
                                message.get("confidence", {})
                            )
                        
                        with st.expander("Safety & Bias Checks", expanded=False):
                            transparency_guardrails.render_safety_checks(message["content"])
                            transparency_guardrails.render_bias_dashboard(message["content"])
                            transparency_guardrails.render_hallucination_detection(message["content"], message.get("sources", []))
                        
                        if message == st.session_state.messages[-1]:
                            st.markdown("**Was this helpful?**")
                            with st.form(key=f"feedback_form_{i}_{hash(message.get('content', ''))}"):
                                col1, col2, col3 = st.columns([1, 2, 1])
                                with col1:
                                    rating = st.selectbox("Rate", [1, 2, 3, 4, 5], index=2, key=f"rating_{i}_{hash(message.get('content', ''))}")
                                with col2:
                                    feedback_text = st.text_input("Feedback", placeholder="Quick feedback...", key=f"feedback_text_{i}_{hash(message.get('content', ''))}")
                                with col3:
                                    submitted = st.form_submit_button("Submit", type="primary")
                                
                                if submitted:
                                    transparency_guardrails.track_learning_feedback(
                                        message.get("query", ""), 
                                        message["content"], 
                                        feedback_text, 
                                        rating
                                    )
                                    st.success("Thanks for your feedback!")
                                    st.rerun()
                        
                        if message.get("sources"):
                            with st.expander("Sources", expanded=False):
                                for source in message["sources"]:
                                    st.write(f"• {source.get('title', 'Unknown')}")
                
                if message["role"] == "assistant":
                    # Only render suggestions for the latest message to improve performance
                    if message == st.session_state.messages[-1]:
                        smart_suggestions.render_follow_up_suggestions(message.get("query", ""), message["content"])

        # Handle clicked suggestions first
        if hasattr(st.session_state, 'suggestion_clicked') and st.session_state.suggestion_clicked:
            prompt = st.session_state.suggestion_clicked
            # Clear the suggestion
            st.session_state.suggestion_clicked = None
        else:
            prompt = st.chat_input("Ask about GitLab...")
        
        if prompt:
            with st.chat_message("user"):
                st.write(prompt)
            
            start_time = datetime.now()
            
            with st.chat_message("assistant"):
                response_placeholder = st.empty()
                response_placeholder.write("Thinking...")
                
                try:
                    response, sources, token_info = chatbot.chat(prompt)
                    
                    response_placeholder.write(response)
                    
                    response_time = (datetime.now() - start_time).total_seconds()
                    smart_suggestions.track_interaction(prompt, response, response_time)
                    
                    performance_monitor.record_query(
                        query=prompt,
                        response_time=response_time,
                        cache_hit=False,
                        confidence_score=0.8,
                        error=None,
                        input_tokens=token_info.get('input_tokens', 0),
                        output_tokens=token_info.get('output_tokens', 0),
                        total_tokens=token_info.get('total_tokens', 0),
                        cost_usd=token_info.get('cost_usd', 0.0)
                    )
                    
                    confidence = transparency_guardrails.calculate_confidence_score(response, sources, prompt)
                    
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": response,
                        "query": prompt,
                        "sources": sources,
                        "confidence": confidence
                    })
                    
                    if sources:
                        with st.expander("Sources", expanded=False):
                            for source in sources:
                                st.write(f"• {source.get('title', 'Unknown')}")
                    
                    smart_suggestions.render_follow_up_suggestions(prompt, response)
                
                except Exception as e:
                    response_placeholder.error(f"Error: {str(e)}")
                    st.session_state.messages.append({"role": "assistant", "content": "I apologize, but I'm having trouble processing your request right now. Please try again."})
    
    def render_setup_interface(self, chatbot_manager, performance_monitor):
        st.title("GitLab AI Assistant")
        st.info("Initializing... Please wait.")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("Setting up components...")
        progress_bar.progress(30)
        
        if chatbot_manager.initialize_chatbot():
            progress_bar.progress(100)
            status_text.text("Ready!")
            st.success("Chatbot initialized successfully!")
            st.rerun()
        else:
            st.error("Failed to initialize chatbot. Please check the configuration.")
    
    def render_sidebar(self, analytics_dashboard, transparency_guardrails, tech_doc_viewer):
        with st.sidebar:
            st.title("GitLab AI Assistant")
            
            if st.button("Chat", use_container_width=True):
                st.session_state.show_chat = True
                st.session_state.show_analytics = False
                st.session_state.show_guardrails = False
                st.session_state.show_docs = False
                st.rerun()
            
            if st.button("Analytics", use_container_width=True):
                st.session_state.show_chat = False
                st.session_state.show_analytics = True
                st.session_state.show_guardrails = False
                st.session_state.show_docs = False
                st.rerun()
            
            if st.button("Guardrails", use_container_width=True):
                st.session_state.show_chat = False
                st.session_state.show_analytics = False
                st.session_state.show_guardrails = True
                st.session_state.show_docs = False
                st.rerun()
            
            if st.button("Documentation", use_container_width=True):
                st.session_state.show_chat = False
                st.session_state.show_analytics = False
                st.session_state.show_guardrails = False
                st.session_state.show_docs = True
                st.rerun()
            
            st.markdown("---")
            
            if hasattr(st.session_state, 'messages') and st.session_state.messages:
                st.metric("Messages", len(st.session_state.messages))
            
            if hasattr(st.session_state, 'learning_feedback') and st.session_state.learning_feedback:
                st.metric("Feedback Entries", len(st.session_state.learning_feedback))
            
            st.markdown("---")
            
            if st.button("Clear Chat", use_container_width=True):
                st.session_state.messages = []
                st.rerun()