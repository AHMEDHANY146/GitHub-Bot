"""
Language management utility for bilingual support (English/Arabic)
"""

from enum import Enum
from typing import Dict, Any
from utils.logger import Logger


class Language(Enum):
    ENGLISH = "en"
    ARABIC = "ar"
    EGYPTIAN = "masri"


class LanguageManager:
    """Manages bilingual text support for the bot"""
    
    def __init__(self):
        self.translations = {
            Language.ENGLISH: {
                # Start and welcome messages
                "welcome_message": """👋 Hello {name}! Welcome to the GitHub README Generator Bot!

I'll help you create a professional GitHub README.md file from your voice or text input.

Here's how it works:
1. 📝 Tell me your name and basic info
2. 🎤 Send a voice message or text about your experience
3. 🤖 I'll extract and structure your information
4. 📄 Generate a beautiful README with Devicon icons
5. 📦 Get it as a ZIP file ready for GitHub!

Ready to start? Let's begin with your name:""",
                
                "lets_start_button": "🚀 Let's Start!",
                "how_it_works_button": "ℹ️ How it Works",
                
                # Help text
                "help_title": "📖 How to Use This Bot",
                "help_steps": """1. Start: Click "Let's Start!" to begin
2. Name: Tell me your full name
3. Your GitHub username: Share your GitHub username
4. Links (optional): LinkedIn, Portfolio, Email
5. Voice/Text: Send a voice message 🎤 or text 📝 describing:
   • Your experience and background
   • Technical skills and programming languages
   • Tools and platforms you use
   • Projects you've worked on

6. Review: I'll show you the extracted information
7. Confirm: Approve and get your README.md file""",
                
                "help_tips": """💡 Tips:
• Speak clearly and include specific technologies
• Mention frameworks, databases, and tools
• The more detail you provide, the better your README
• Voice messages work best for natural descriptions

🔧 Supported Languages:
Python, JavaScript, React, Docker, Git, AWS, and many more!

Ready? Click "Let's Start!" below!""",
                
                # Collection prompts
                "start_collection": """Great! Let's start building your README.

First, what's your full name? 📝

Please type your name as you'd like it to appear on your GitHub profile.""",
                
                "name_saved": "✅ Great! Your name is: {name}\n\nWhat's your GitHub username? (required)\nThis will be used for GitHub stats and profile links.",
                "github_saved": "✅ GitHub username saved: {github}\n\nWhat's your LinkedIn profile URL? (optional)",
                "linkedin_saved": "✅ LinkedIn profile saved\n\nWhat's your portfolio website URL? (optional)",
                "portfolio_saved": "✅ Portfolio saved\n\nWhat's your email address? (optional)",
                
                # Experience collection
                "experience_prompt": """Perfect! Thanks {name}! 🎉

Now, tell me about your experience and skills. You can:

🎤 Send a voice message
📝 Type a text description

Tell me about:
• Your professional background
• Programming languages and frameworks
• Tools and platforms you work with
• Notable projects or achievements

The more detail you provide, the better your README will be!""",
                
                # Processing
                "processing": """🔄 Processing your information...

I'm analyzing your experience and extracting:
• Technical skills
• Programming languages  
• Tools and platforms
• Professional summary

This will take a few moments...""",
                
                # Validation messages
                "invalid_name": "❌ Please enter a valid name (2-50 characters, letters only).\nWhat's your full name?",
                "invalid_github": "❌ Please enter a valid GitHub username.\nGitHub usernames are 1-39 characters, alphanumeric and hyphens only.\nWhat's your GitHub username? (required)",
                "invalid_linkedin": "❌ Please enter a valid LinkedIn URL.\nExample: https://linkedin.com/in/yourname\nWhat's your LinkedIn URL? (or click Skip)",
                "invalid_portfolio": "❌ Please enter a valid portfolio URL.\nExample: https://yourname.github.io or https://yourportfolio.com\nWhat's your portfolio URL? (or click Skip)",
                "invalid_email": "❌ Please enter a valid email address.\nWhat's your email address? (or click Skip)",
                "invalid_experience": "❌ Please provide more details about your experience (at least 50 characters).\n\nTell me about:\n• Your background and experience\n• Technical skills and programming languages\n• Tools and platforms you use\n• Projects you've worked on\n\nYou can also send a voice message instead!",
                
                # Skip button
                "skip_button": "⏭️ Skip",
                "skipped_linkedin": "✅ Skipped LinkedIn\n\nWhat's your portfolio website URL? (optional)",
                "skipped_portfolio": "✅ Skipped portfolio\n\nWhat's your email address? (optional)",
                
                # Language selection
                "language_prompt": "Please select your preferred language / من فضلك اختر لغتك المفضلة:",
                "language_english": "🇺🇸 English",
                "language_arabic": "🇸🇦 العربية",
                
                # General
                "not_sure": "I'm not sure what you want to do. Please use /start to begin.",
                
                # Confirmation buttons
                "approve_button": "✅ Approve & Generate",
                "edit_button": "✏️ Edit Skills", 
                "regenerate_button": "🔄 Regenerate",
                "cancel_button": "❌ Cancel",
                
                # Confirmation messages
                "confirmation_text": """📋 Review Your Information

Name: {name}

About Me:
{summary}

Skills ({len(skills)}):
{', '.join(skills[:10])}{'...' if len(skills) > 10 else ''}

Tools ({len(tools)}):
{', '.join(tools[:10])}{'...' if len(tools) > 10 else ''}

Languages ({len(languages)}):
{', '.join(languages[:10])}{'...' if len(languages) > 10 else ''}""",
                
                "confirmation_prompt": "Is this information correct? Choose an option below:",
                "edit_prompt": """✏️ Edit Your Information

Please send me a corrected version of your experience. You can:

🎤 Send a new voice message, or
📝 Type a text description

Focus on any skills, tools, or languages I might have missed.""",
                
                "regenerate_message": "🔄 Regenerating your README...",
                "cancel_message": """❌ README Generation Cancelled

Your session has been cleared. 

If you'd like to try again, just send /start to begin a new conversation!""",
                
                # Voice handler messages
                "please_complete_previous_steps": "Please complete the previous steps first. Use /start to begin.",
                "processing_voice_message": "🎤 Processing your voice message...",
                "voice_transcription_failed": """❌ Sorry, I couldn't understand your voice message. 
This could be due to:
• Poor audio quality
• Background noise
• Unsupported audio format

Please try again speaking clearly or type your experience instead.""",
                "voice_processing_error": "❌ An error occurred while processing your voice message",
                "no_experience_data": "❌ No experience data found. Please try again.",
                "structured_extraction_failed": "❌ I couldn't extract structured information from your input. Please provide more details about your skills and experience.",
                "processing_error": "❌ An error occurred while processing your information. Please try again or contact support.",
                "processing_information": """🔄 Processing your information

I'm analyzing your experience and extracting:
• Technical skills
• Programming languages  
• Tools and platforms
• Professional summary

This will take a few moments""",
                
                # Rating and feedback system
                "rating_prompt": """⭐ Rate Your Experience!

Did you like the bot? We'd love to hear your feedback about the README creation experience!

🌟 Choose your rating from 5 stars:""",
                "rating_skip": "Skip",
                "rating_thanks_5": """🎉 Thank you for your {stars} rating!

We're so glad you liked the service! 💫

💬 Do you have any suggestions or feedback?
Share your thoughts to help us improve the bot!

💝 Support the Developer:
If you liked the service, you can support the developer via:
https://ipn.eg/S/ahmedhanycs/instapay/5Ni1NH

Every support is appreciated and helps us provide better service! 🙏""",
                "rating_thanks_4_3": """👍 Thank you for your {stars} rating!

We appreciate your feedback and we're always striving to improve! 📈

💬 Do you have suggestions for improvement?
We'd love to hear your ideas to make the bot better!

💝 Support the Developer:
https://ipn.eg/S/ahmedhanycs/instapay/5Ni1NH""",
                "rating_thanks_1_2": """📝 Thank you for your {stars} rating

We're sorry if the experience wasn't as expected! 😔

🔧 Contact the developer directly:
@Ahmedhany146

They will personally help you solve any issues or improve your experience! 🚀""",
                "feedback_prompt": """💬 Share Your Thoughts!

Write your suggestions or comments here:

✨ What did you like?
🔧 What could be improved?
💡 New ideas?

Your feedback helps us grow! 🚀""",
                "feedback_thanks": """🎉 Thank you so much for your feedback!

Your opinion matters greatly and will help us improve! 📈

💝 Support the Developer:
If you liked the service, you can support development via:
https://ipn.eg/S/ahmedhanycs/instapay/5Ni1NH

🔧 For any inquiries:
@Ahmedhany146

Thank you for your trust! 🙏"""
            },
            
            Language.ARABIC: {
                # Start and welcome messages
                "welcome_message": """👋 أهلاً {name}! مرحباً بك في بوت مولد ملفات GitHub README!

سأساعدك في إنشاء ملف GitHub README.md احترافي من رسالتك الصوتية أو النصية.

إليك كيفية العمل:
1. 📝 أخبرني باسمك ومعلوماتك الأساسية
2. 🎤 أرسل رسالة صوتية أو نص عن خبرتك
3. 🤖 سأقوم باستخراج وتنظيم معلوماتك
4. 📄 إنشاء README جميل مع أيقونات Devicon
5. 📦 احصل عليه كملف ZIP جاهز لـ GitHub!

هل أنت مستعد للبدء؟ دعنا نبدأ باسمك:""",
                
                "lets_start_button": "🚀 هيا نبدأ!",
                "how_it_works_button": "ℹ️ كيف يعمل",
                
                # Help text
                "help_title": "📖 كيفية استخدام هذا البوت",
                "help_steps": """1. البدء: انقر على "هيا نبدأ!" للبدء
2. الاسم: أخبرني باسمك الكامل
3. اسم المستخدم في GitHub: شاركنا اسم مستخدم GitHub الخاص بك
4. الروابط (اختياري): LinkedIn, Portfolio, Email
5. صوت/نص: أرسل رسالة صوتية 🎤 أو نص 📝 تصف:
   • خبرتك وخلفيتك
   • المهارات التقنية ولغات البرمجة
   • الأدوات والمنصات التي تستخدمها
   • المشاريع التي عملت عليها

6. المراجعة: سأعرض لك المعلومات المستخرجة
7. التأكيد: وافق واحصل على ملف README.md الخاص بك""",
                
                "help_tips": """💡 نصائح:
• تحدث بوضوح واشمل التقنيات المحددة
• اذكر الأطر، قواعد البيانات، والأدوات
• كلما زادت التفاصيل، كان README أفضل
• الرسائل الصوتية تعمل بشكل أفضل للوصف الطبيعي

🔧 اللغات المدعومة:
Python, JavaScript, React, Docker, Git, AWS, والعديد أكثر!

هل أنت مستعد؟ انقر على "هيا نبدأ!" بالأسفل!""",
                
                # Collection prompts
                "start_collection": """رائع! دعنا نبدأ في بناء README الخاص بك.

أولاً، ما هو اسمك الكامل؟ 📝

يرجى كتابة اسمك كما تظهر في ملفك الشخصي على GitHub.""",
                
                "name_saved": "✅ رائع! اسمك هو: {name}\n\nما هو اسم مستخدم GitHub الخاص بك؟ (مطلوب)\nسيتم استخدامه لإحصائيات GitHub وروابط الملف الشخصي.",
                "github_saved": "✅ تم حفظ اسم مستخدم GitHub: {github}\n\nما هو رابط ملفك الشخصي في LinkedIn؟ (اختياري)",
                "linkedin_saved": "✅ تم حفظ ملف LinkedIn الشخصي\n\nما هو رابط موقعك الإلكتروني؟ (اختياري)",
                "portfolio_saved": "✅ تم حفظ الموقع الإلكتروني\n\nما هو عنوان بريدك الإلكتروني؟ (اختياري)",
                
                # Experience collection
                "experience_prompt": """مثالي! شكراً {name}! 🎉

الآن، أخبرني عن خبرتك ومهاراتك. يمكنك:

🎤 إرسال رسالة صوتية
📝 كتابة وصف نصي

أخبرني عن:
• خلفيتك المهنية
• لغات البرمجة والأطر
• الأدوات والمنصات التي تعمل معها
• المشاريع البارزة أو الإنجازات

كلما زادت التفاصيل التي تقدمها، كان README أفضل!""",
                
                # Processing
                "processing": """🔄 جاري معالجة معلوماتك...

أنا أحلل خبرتك وأستخرج:
• المهارات التقنية
• لغات البرمجة  
• الأدوات والمنصات
• الملخص المهني

سيستغرق هذا بضع لحظات...""",
                
                # Validation messages
                "invalid_name": "❌ يرجى إدخال اسم صحيح (2-50 حرفاً، أحرف فقط).\nما هو اسمك الكامل؟",
                "invalid_github": "❌ يرجى إدخال اسم مستخدم GitHub صحيح.\nأسماء مستخدمي GitHub هي 1-39 حرفاً، أبجدية رقمية وشرطات فقط.\nما هو اسم مستخدم GitHub الخاص بك؟ (مطلوب)",
                "invalid_linkedin": "❌ يرجى إدخال رابط LinkedIn صحيح.\nمثال: https://linkedin.com/in/yourname\nما هو رابط LinkedIn الخاص بك؟ (أو انقر على تخطي)",
                "invalid_portfolio": "❌ يرجى إدخال رابط موقع إلكتروني صحيح.\nمثال: https://yourname.github.io أو https://yourportfolio.com\nما هو رابط موقعك الإلكتروني؟ (أو انقر على تخطي)",
                "invalid_email": "❌ يرجى إدخال عنوان بريد إلكتروني صحيح.\nما هو عنوان بريدك الإلكتروني؟ (أو انقر على تخطي)",
                "invalid_experience": "❌ يرجى تقديم المزيد من التفاصيل عن خبرتك (50 حرفاً على الأقل).\n\nأخبرني عن:\n• خلفيتك وخبرتك\n• المهارات التقنية ولغات البرمجة\n• الأدوات والمنصات التي تستخدمها\n• المشاريع التي عملت عليها\n\nيمكنك أيضاً إرسال رسالة صوتية بدلاً من ذلك!",
                
                # Skip button
                "skip_button": "⏭️ تخطي",
                "skipped_linkedin": "✅ تم تخطي LinkedIn\n\nما هو رابط موقعك الإلكتروني؟ (اختياري)",
                "skipped_portfolio": "✅ تم تخطي الموقع الإلكتروني\n\nما هو عنوان بريدك الإلكتروني؟ (اختياري)",
                
                # Language selection
                "language_prompt": "من فضلك اختر لغتك المفضلة / Please select your preferred language:",
                "language_english": "🇺🇸 English",
                "language_arabic": "🇸🇦 العربية",
                
                # General
                "not_sure": "لست متأكداً مما تريد القيام به. يرجى استخدام /start للبدء.",
                
                # Confirmation buttons
                "approve_button": "✅ موافق وتوليد",
                "edit_button": "✏️ تعديل المهارات", 
                "regenerate_button": "🔄 إعادة التوليد",
                "cancel_button": "❌ إلغاء",
                
                # Confirmation messages
                "confirmation_text": """📋 مراجعة معلوماتك

الاسم: {name}

عني:
{summary}

المهارات ({len(skills)}):
{', '.join(skills[:10])}{'...' if len(skills) > 10 else ''}

الأدوات ({len(tools)}):
{', '.join(tools[:10])}{'...' if len(tools) > 10 else ''}

اللغات ({len(languages)}):
{', '.join(languages[:10])}{'...' if len(languages) > 10 else ''}""",
                
                "confirmation_prompt": "هل هذه المعلومات صحيحة؟ اختر خياراً أدناه:",
                "edit_prompt": """✏️ تعديل معلوماتك

يرجى إرسال نسخة مصححة من خبرتك. يمكنك:

🎤 إرسال رسالة صوتية جديدة، أو
📝 كتابة وصف نصي

ركز على أي مهارات أو أدوات أو لغات قد تكون فاتني.""",
                
                "regenerate_message": "🔄 إعادة توليد README الخاص بك...",
                "cancel_message": """❌ تم إلغاء توليد README

تم مسح جلستك. 

إذا كنت ترغب في المحاولة مرة أخرى، فقط أرسل /start لبدء محادثة جديدة!""",
                
                # Voice handler messages
                "please_complete_previous_steps": "يرجى إكمال الخطوات السابقة أولاً. استخدم /start للبدء.",
                "processing_voice_message": "🎤 جاري معالجة رسالتك الصوتية...",
                "voice_transcription_failed": """❌ آسف، لم أتمكن من فهم رسالتك الصوتية.
قد يكون السبب:
• جودة الصوت السيئة
• الضوضاء في الخلفية
• صيغة صوتية غير مدعومة

يرجى المحاولة مرة أخرى بالتحدث بوضوح أو كتابة خبرتك بدلاً من ذلك.""",
                "voice_processing_error": "❌ حدث خطأ أثناء معالجة رسالتك الصوتية",
                "no_experience_data": "❌ لم يتم العثور على بيانات الخبرة. يرجى المحاولة مرة أخرى.",
                "structured_extraction_failed": "❌ لم أتمكن من استخراج معلومات منظمة من مدخلاتك. يرجى تقديم المزيد من التفاصيل حول مهاراتك وخبرتك.",
                "processing_error": "❌ حدث خطأ أثناء معالجة معلوماتك. يرجى المحاولة مرة أخرى أو التواصل مع الدعم.",
                "processing_information": """🔄 جاري معالجة معلوماتك

أنا أحلل خبرتك وأستخرج:
• المهارات التقنية
• لغات البرمجة  
• الأدوات والمنصات
• الملخص المهني

سيستغرق هذا بضع لحظات""",
                
                # Rating and feedback system
                "rating_prompt": """⭐ قيم تجربتك!

هل أعجبك البوت؟ يسعدنا أن نعرف رأيك في تجربة إنشاء README!

🌟 اختر تقييمك من 5 نجوم:""",
                "rating_skip": "تخطي",
                "rating_thanks_5": """🎉 شكراً لتقييمك {stars}!

يسعدنا جداً أنك أعجبت بالخدمة! 💫

💬 هل لديك أي اقتراحات أو فيدباك؟
شاركنا رأيك لتطوير البوت!

💝 دعم المطور:
إذا أحببت الخدمة، يمكنك دعم المطور عبر:
https://ipn.eg/S/ahmedhanycs/instapay/5Ni1NH

كل دعم يقدر ويساعدنا على تقديم خدمة أفضل! 🙏""",
                "rating_thanks_4_3": """👍 شكراً لتقييمك {stars}!

يسعدنا رأيك ونحن نسعى للتحسين المستمر! 📈

💬 هل لديك اقتراحات للتحسين؟
نحب أن نسمع أفكارك لجعل البوت أفضل!

💝 دعم المطور:
https://ipn.eg/S/ahmedhanycs/instapay/5Ni1NH""",
                "rating_thanks_1_2": """📝 شكراً لتقييمك {stars}

نأسف إذا لم تكن التجربة كما تتوقع! 😔

🔧 تواصل مع المطور مباشرة:
@Ahmedhany146

سيساعدك شخصياً في حل أي مشكلة أو تحسين تجربتك! 🚀""",
                "feedback_prompt": """💬 شاركنا رأيك!

اكتب لنا اقتراحاتك أو ملاحظاتك هنا:

✨ ما الذي أعجبك؟
🔧 ما الذي يمكن تحسينه؟
💡 أفكار جديدة؟

مشاركتك تساعدنا على التطور! 🚀""",
                "feedback_thanks": """🎉 شكراً جزيلاً على مشاركتك!

رأيك يهمنا جداً وسيساعدنا على التحسين! 📈

💝 دعم المطور:
إذا أحببت الخدمة، يمكنك دعم التطوير عبر:
https://ipn.eg/S/ahmedhanycs/instapay/5Ni1NH

🔧 لأي استفسار:
@Ahmedhany146

شكراً لثقتك بنا! 🙏"""
            },

            Language.EGYPTIAN: {
                # Start and welcome messages
                "welcome_message": """👋 أهلاً يا بطل {name}! منورنا في بوت GitHub README! 😎

هساعدك تعمل ملف README.md احترافي لبروفايلك من صوتك أو كلامك.

الموضوع بسيط:
1. 📝 هنعرف اسمك وبياناتك الأولية
2. 🎤 ابعت فويس أو اكتب عن خبرتك ومشاريعك
3. 🤖 هظبطلك كل المعلومات دي بشكل منظم
4. 📄 هعملك README شيك جداً بأيقونات Devicon
5. 📦 هتستلمه ملف ZIP ترفعه علطول على GitHub!

جاهز يا بطل؟ يلا نبدأ باسمك:""",
                
                "lets_start_button": "🚀 يلا بينا نبدأ!",
                "how_it_works_button": "ℹ️ إزاي بيشتغل؟",
                
                # Help text
                "help_title": "📖 إزاي تستخدم البوت",
                "help_steps": """1. البداية: دوس على "يلا بينا نبدأ!"
2. الاسم: عرفنا بنفسك (الاسم بالكامل)
3. يوزر GitHub: عشان نحط لينكاتك وتظهر إحصائياتك
4. لينكات تانية (اختياري): LinkedIn, Portfolio, Email
5. الفويس/الكتابة: ابعت فويس 🎤 أو اكتب 📝 فيها:
   • خبرتك اشتغلت فين وإيه
   • اللغات والمهارات التقنية اللي تعرفها
   • الأدوات اللي بتستخدمها (Docker, AWS, etc)
   • مشاريع عملتها وفخور بيها

6. المراجعة: هوريك كل اللي جمعته عنك
7. التأكيد: وافق واستلم ملفك يا معلم!""",
                
                "help_tips": """💡 نصائح عشان الملف يطلع جامد:
• اتكلم بوضوح وقول أسماء التكنولوجي صح
• اذكر الفريم ووركس وقواعد البيانات
• كل ما تحكى تفاصيل أكتر، الملف هيطلع أغنى
• الفويس بيكون أسهل وأسرع ليك

🔧 اللغات اللي بدعمها:
Python, JavaScript, React, Docker, Git, AWS, وكله!

جاهز؟ دوس "يلا بينا نبدأ!" تحت!""",
                
                # Collection prompts
                "start_collection": """عاش! يلا نبني الـ README بتاعك.

أول حاجة، اسمك إيه بالكامل؟ 📝

اكتب الاسم اللي عايزة يظهر في بروفايلك.""",
                
                "name_saved": "✅ تمام يا {name}! اسمك زي الفل.\n\nإيه بقى الـ GitHub Username بتاعك؟ (ده ضروري)\nعشان نظهر إحصائياتك ونربط البروفايل.",
                "github_saved": "✅ تمام الـ GitHub: {github}\n\nطيب عندك LinkedIn؟ ابعت اللينك بتاعه (اختياري)",
                "linkedin_saved": "✅ الـ LinkedIn تمام\n\nعندك موقع شخصي (Portfolio)؟ (اختياري)",
                "portfolio_saved": "✅ الموقع تمام\n\nطيب الإيميل بتاعك إيه؟ (اختياري)",
                
                # Experience collection
                "experience_prompt": """زي الفل يا {name}! 🎉

دلوقتي بقى أهم جزء.. احكيلي عن خبرتك ومهاراتك. تقدر:

🎤 تبعت فويس (أسهل وأسرع)
📝 أو تكتبلي وصف

احكيلي عن:
• اشتغلت فين قبل كدة
• تكنولوجي بتستخدمها (لغات، فريم ووركس)
• أدوات بتستخدمها في شغلك
• مشاريع عملتها

خد راحتك في الكلام، كل ما تحكي أكتر، الملف هيطلع أحلى!""",
                
                # Processing
                "processing": """🔄 بظبطلك المعلومات...

دلوقتي بحلل كلامك وبطلع منه:
• مهاراتك التقنية
• لغات البرمجة
• الأدوات اللي بتستخدمها
• وبكتبلك ملخص احترافي عنك

ثواني والكل يكون جاهز...""",
                
                # Validation messages
                "invalid_name": "❌ الاسم مش مظبوط (لازم يكون حروف ومن 2 لـ 50 حرف).\nاسمك إيه بالكامل؟",
                "invalid_github": "❌ يوزر GitHub مش صح.\nلازم يكون حروف وأرقام وشرطات بس.\nإيه هو يوزر GitHub بتاعك؟ (ضروري)",
                "invalid_linkedin": "❌ لينك LinkedIn مش مظبوط.\nمثال: https://linkedin.com/in/yourname\nإيه لينك LinkedIn بتاعك؟ (أو دوس تخطي)",
                "invalid_portfolio": "❌ لينك الموقع مش مظبوط.\nمثال: https://yourname.github.io\nإيه لينك موقعك؟ (أو دوس تخطي)",
                "invalid_email": "❌ الإيميل مش مظبوط.\nإيه هو إيميلك؟ (أو دوس تخطي)",
                "invalid_experience": "❌ محتاج تفاصيل أكتر شوية (على الأقل 50 حرف).\n\nاحكيلي عن:\n• خبرتك وشغلك\n• التكنولوجي اللي عارفها\n• المشاريع اللي عملتها\n\nممكن تبعت فويس أسهل!",
                
                # Skip button
                "skip_button": "⏭️ تخطي",
                "skipped_linkedin": "✅ ماشي، تخطي LinkedIn\n\nعندك موقع شخصي Portfolio؟ (اختياري)",
                "skipped_portfolio": "✅ تخطي الموقع\n\nطيب إيميلك إيه؟ (اختياري)",
                
                # Language selection
                "language_prompt": "اختار اللغة اللي تريحك / Choose your language:",
                "language_english": "🇺🇸 English",
                "language_arabic": "🇸🇦 العربية",
                "language_egyptian": "🇪🇬 مصري",
                
                # General
                "not_sure": "مش فاهم قصدك أوي. ابعت /start عشان نبدأ من الأول.",
                
                # Confirmation buttons
                "approve_button": "✅ تمام، اعتمد!",
                "edit_button": "✏️ تعديل المهارات", 
                "regenerate_button": "🔄 جرب تاني",
                "cancel_button": "❌ إلغاء",
                
                # Confirmation messages
                "confirmation_text": """📋 راجع بياناتك يا بطل

الاسم: {name}

نبذة عني:
{summary}

المهارات ({len(skills)}):
{', '.join(skills[:10])}{'...' if len(skills) > 10 else ''}

الأدوات ({len(tools)}):
{', '.join(tools[:10])}{'...' if len(tools) > 10 else ''}

اللغات ({len(languages)}):
{', '.join(languages[:10])}{'...' if len(languages) > 10 else ''}""",
                
                "confirmation_prompt": "الكلام ده مظبوط؟ اختار من تحت:",
                "edit_prompt": """✏️ عدل براحتك

ابعتلي التصحيح اللي عايزه. ممكن:

🎤 تبعت فويس جديد
📝 أو تكتبلي التعديل

قولي لو في مهارات أو أدوات نسيتها.""",
                
                "regenerate_message": "🔄 بظبطلك الـ README تاني...",
                "cancel_message": """❌ تم الإلغاء

خلاص مسحت الجلسة دي.

لو عايز تبدأ من جديد في أي وقت، ابعت /start.""",
                
                # Voice handler messages
                "please_complete_previous_steps": "كمل الخطوات اللي فاتت الأول. ابعت /start عشان تبدأ.",
                "processing_voice_message": "🎤 بسمع الفويس...",
                "voice_transcription_failed": """❌ سوري، مسمعتش الفويس كويس.
ممكن يكون بسبب:
• الصوت واطي أو مش واضح
• دوشة جنبك
• صيغة الملف مش تمام

جرب تبعت تاني بصوت أوضح أو اكتبلي كتابة.""",
                "voice_processing_error": "❌ حصلت مشكلة وأنا بفك الفويس",
                "no_experience_data": "❌ ملقيتش بيانات خبرة. جرب تاني.",
                "structured_extraction_failed": "❌ معرفتش اطلع معلومات منظمة من الكلام. وضحلي أكتر مهاراتك وخبرتك.",
                "processing_error": "❌ حصلت مشكلة في المعالجة. جرب تاني أو كلم الدعم.",
                "processing_information": """🔄 بظبطلك المعلومات...

بحلل كلامك وبطلع منه:
• مهاراتك التقنية
• لغات البرمجة
• الأدوات والمنصات

لحظات ويكون جاهز...""",
                
                # Rating and feedback system
                "rating_prompt": """⭐ إيه رأيك في البوت؟

عجبتك التجربة؟ يهمنا جداً نعرف رأيك!

🌟 قيمنا من 5 نجوم:""",
                "rating_skip": "تخطي",
                "rating_thanks_5": """🎉 تسلم على تقييمك {stars}!

مبسوطين جداً إن البوت عجبك! 💫

💬 عندك أي اقتراحات أو ملاحظات؟
قولنا رأيك عشان نطور البوت أكتر!

💝 دعم المطور:
لو الخدمة عجبتك، ممكن تدعم المطور:
https://ipn.eg/S/ahmedhanycs/instapay/5Ni1NH

كل دعم بيفرق معانا جداً! 🙏""",
                "rating_thanks_4_3": """👍 شكراً على تقييمك {stars}!

رأيك ع راسنا وبنحاول دايماً نتحسن! 📈

💬 عندك اقتراحات للتطوير؟
يا ريت تقولنا عشان نخلي البوت أحسن!

💝 دعم المطور:
https://ipn.eg/S/ahmedhanycs/instapay/5Ni1NH""",
                "rating_thanks_1_2": """📝 شكراً على تقييمك {stars}

آسفين لو التجربة كانت مش قد كدة! 😔

🔧 كلم المطور مباشرة:
@Ahmedhany146

وهو هيظبطلك الدنيا ويحل أي مشكلة! 🚀""",
                "feedback_prompt": """💬 قولنا رأيك بصراحة!

اكتب اقتراحاتك أو ملاحظاتك هنا:

✨ إيه اللي عجبك؟
🔧 إيه اللي محتاج يتظبط؟
💡 عندك أفكار جديدة؟

رأيك بيساعدنا نكبر! 🚀""",
                "feedback_thanks": """🎉 متشكرين جداً على وقتك!

رأيك ده غالي علينا وهيساعدنا نحسن الخدمة! 📈

💝 دعم المطور:
لو حبيت الشغل، ممكن تدعمنا:
https://ipn.eg/S/ahmedhanycs/instapay/5Ni1NH

🔧 لو عندك استفسار:
@Ahmedhany146

شكراً ليك يا بطل! 🙏"""
            }
        }
    
    def get_text(self, key: str, language: Language = Language.ENGLISH, **kwargs) -> str:
        """Get translated text with optional string formatting"""
        try:
            text = self.translations[language].get(key, self.translations[Language.ENGLISH].get(key, key))
            if kwargs:
                return text.format(**kwargs)
            return text
        except Exception as e:
            logger = Logger.get_logger(__name__)
            logger.error(f"Error getting translation for key '{key}': {e}")
            return key
    
    def get_language_from_code(self, language_code) -> Language:
        """Convert language code string to Language enum"""
        try:
            # Handle both string and Language enum inputs
            if isinstance(language_code, Language):
                return language_code
            elif isinstance(language_code, str):
                return Language(language_code.lower())
            else:
                return Language.ENGLISH
        except ValueError:
            return Language.ENGLISH


# Global instance
language_manager = LanguageManager()
