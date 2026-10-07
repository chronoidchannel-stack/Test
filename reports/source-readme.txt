Info/ReimuSanae Rig Readme.docx
Reimu&Sanae Rig 
Thanks for Downloading Sanae Rig!!
This is an expansion from the original Reimu rig, the rig shares the same control scheme and set up plus new quality of life feature and more clothing options! It has been tested with various animators and I think it is time to release it to the public. I am excited to see what people create with the rig! Feel free to use the rig for any non commercial use as long as you mention me in the credit!

If you find anything broken or have suggestions, please don't hesitate to reach out to me.Or give this doc a quick read, there could be an answer to your problem written here.If you like the rig, feel free to check my other rig on gumroad!“https://gumroad.com/megabubu”Toon shader is create with a combination of few other shader I found online, special thanks toEnogu Toon shader and Kodde Toon shader

**Quick disclaimer about the rig**
**This is not a game ready rig, and it can be quite heavy compared to a simple game rig, there are multiple ways to make it less heavy, like turning off facial expression rig, hide outline layer or use proxy model.**This character is meant to be animated in viewport 2.0, material and shader are built using ShaderFX, it allow you to see exactly what she should look like in viewport without rendering ( you can still render her out using maya hardware 2.0)**The scene currently has one default light, that light, the shader may not support multiple lights like normal material, there is a version of the rig that is just normal lambert material, in case people want to have more flexibility with lighting. “Sanae_Rig_master_nontoon.ma”**Known issue**Maya crash or the model stop following the rigBecause the toon shader was made using ShaderFX, there seems to be few issues when maya is in parallel mode. If you get multiple crashes or see the rig model stop following the rig, try switching to “DG” Evaluation and see if that solves the problem. This problem may relate to how maya was set up or the performance of the machine.

Material doesnt behave correctly
If the model is shown black or the crosshatch and pattern doesn't show up on the model, it is likely that maya cannot find the path to the texture, What you can do is to make sure you set project to the rig folder or make sure your animation scene ( That you import the rig into ) is in the same directory as the rig and texture files





Rig Features
This character is based on the character name Reimu Hakurei, If you don't already know her, she is a shrine maiden who beat up demons that may or may not have done terrible stuff.All you need to know is she kicks ass, and can fly.
Options Control
Most of the rig controls and geometry visibility toggle are in options control above the character's head.You can use this to only show set of control that you are working on, most facial controls are broken down to primary and secondary, for general blocking purpose, you can hide all secondary controls which are meant for small tweaksThe attribute list can be long but they are straight forward, try them out!!
You can adjust the outline width using “Outline Width” Attribute.You can now adjust the size of the cross hatch and screentone pattern using  Attribute

You can switch the rig to casual mode where the character looks more generic and would support more shot types. For Reimu rig, hide all the clothing and the dangling hair bits then toggle “Body Casual” to 1Sanae rig do have casual body as well but she also comes with more uniform options( use picker to quickly swap clothing set )


Proxy Version of the rig can be toggle here


This is also where you toggle the prop rig on and off


Global Scale can be found on the top node of the rig


Spine
Her spine set up is a hybrid IKFK setup where IK controls works on top of FK control( this means rotating FK control would also move IK control) I find this easier to use than having to switch between two mode, you may also toggle the micro control to tweak each joint of the spine individuallyThere are two controls for the hip each have different pivots, use “hip_01” to rotate the hip from higher up and use “hip_01_micro_ctrl” to rotate at the hip joint.All the option for spine set up are stored in “cog_secondary_ctrl”



Arm and Leg

Arm and leg have similar set up, there will be a pin shape control “L&R_arm_option_ctrl” “L&R_leg_option_ctrl” at the end of the limb which stores the IKFK switch attribute. 
Control VisibilityThere you can toggle the visibility of the bendy control, there are two set of bendy, use “Bendy Ctrl” for general tweak, but if you want absolute control over every joint, then use “Micro Ctrl”IK and FK control will be visible and hide based on which mode you are using, but you may also manually show or hide them. By turning “Auto Visibility” off.
Elbow and Knee Offset
Use “L_elbow_offset_ctrl”, “L_knee_offset_ctrl” to offset the elbow and knee position, this will work on both IK and FK mode.





IK FK Matching
IKFK matching can be done using a command button in the picker, how it works is you will have to first select the option control of the limb you wish to match, then press one of the command button to execute the matching

Hand
Use the same arm option control to toggle finger control visibility.You may also try to use a quick finger posing attribute by translating and rotating the pin, they are tied to a common finger pose, they are very useful to animate on top of a posed finger as overall movement.
Foot
Foot AttributeMost of the common reverse IK foot attribute are tied to the quad arrow control at the ankle “IK_foot_option_ctrl”Translate it forward and backward for foot roll, translate it side to side for foot tilt, and etc.They are tied to basic manipulators, so they can be accessed easily.


Hair
Overall Hair Posing
Similar to quick finger attribute, you can use the floating “hair master control” to animate overall hair movement for each zone of the hair, bang, side wisk, ponytail and the long hair in the back.

Specific Hair PosingTo tweak every joint individually, use secondary hair controls



Clothing
Each part of the clothing have tweak control, they are pretty straight forwardThe most complicated one would be the skirt which has more complex features.

Overall Skirt PosingUse the “skirt_master_ctrl” at the bottom of the skirt to pose overall skirt and get access to more options.


Skirt Auto Collide
If you toggle “Auto Collide” attribute on, the rig will try its best to offset the skirt away from the legs. You may slide the attribute back to 0 to resume total control of the skirt and animate the collision manually. Or blend between the two.

Facial

Facial controls are pretty straight forward, but the part that is worth mentioning would be the lip corner and teethIn the 2022 version. The head also has squash and stretch features.

Head squash and stretch

Lip corner

Lip Corner Auto Relax
As you open the jaw, the lip will auto relax itself based on the weight you set ( the lip corner on the screen right is set to relax as the jaw rotates down. You may also turn this off if you want total control.


Lip Corner Attribute
Use “Corner Relax” to rotate upper and lower lip corner away from each otherUse “Corner Spread” to translate upper and lower lip corner away from each other
Sticky Lip
Use “StickyLip” attribute to zip the lip shut wherever the lip pose is, zip both sides up and the mouth will be completely shut while maintaining the mouth pose.
Jaw control

Jaw Follow Weight

On jaw control, you may set the weight that controls how much main lip controls follow the jaw movement, set it to 0 and the lip will not follow jaw at all, set it to 1, to have the lip move 1-1 with the jaw. Lip corner is set to move half way with the jaw by default.
Teeth

On jaw control, you may switch the teeth between two mode, separate teeth mode on the leftAnd combine mode on the right, combine mode will be just a plane with a line across it, just like how anime teeth crunch is normally drawn.Upper and lower Teeth can now follow the mouth master control for easy posing

Eyeball
The highlight on the eyeball is just a floating geometry, you can shape them and place them elsewhere.Set highlight follow at 1 if you want to lock the highlight position on the eyeball


Emote Patch

Emote patch is a set of sprite that can assist certain anime style facial expressionsUse “emote_master_ctrl” to toggle visibility of each patch

Example



Picker

Included with the rig is the animschool picker for the body and the face( special thanks to Leonado Quert for helping me setting this up :) )If the picker doesn't work, make sure you check the namespace edit in the animschool picker tab

