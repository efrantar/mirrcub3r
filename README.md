mirrcub3r
=========

This repository contains the full source-code of *mirrcub3r*, the first ever Lego (Mindstorms) robot to solve a (randomly scrambled) Rubik's Cube in under 1 second. With an average solving time of around 1.2 seconds, it is currently (November 2019) also the fastest Lego-based solver in the world.

![](https://github.com/efrantar/mirrcub3r/blob/master/sub1.gif)

More detailed videos showcasing mirrcub3r can be found here: TODO (improved version), https://www.youtube.com/watch?v=03V3915YuB4 (initial version, ~1.5s average)

# Details

The robot is driven by 3 Lego Mindstorms EV3 bricks driving a total of 10 medium motors. 2 motors each are combined with additional gearing to achieve higher speeds and more turning power. Mirrcub3r's name comes from the the fact that it uses 4 small mirrors precisely positioned so that a single smartphone camera can see all 6 sides of the cube at once, thus enabling ~5 millisecond scanning times (to the best of my knowledge, this is the first cube-solver to employ such a mirror system). The robot connecting directly to the centers of the cube-faces is enabled by glueing "2x2 Plate Round" bricks on the cube's (a well lubed and relatively tightly tensioned GAN 356 R) center caps. Some people might consider this cheating, however all recent (non-Lego) official Guinness World Records also feature robots that require some modifications of the cube centers. The robot can only turng 5 faces of the cube, this is however sufficient to solve all possible scrambles (with ~12% average move penalty). Solutions are computed by my own highly-optimized `rob-twophase` solver in `-DQUARTER -DAXIAL -DFACES5` mode. It not only fully utilizes all 6 cores / 12 threads of an AMD Ryzen 3600 but is also specifically written to find solutions that are particularly efficient to execute for mirrcub3r (for example containing many consecutive moves on parallel faces which can be performed at the same time). The robot is controlled via Lego Mindstorm Direct commands (compiled bit-patterns accepted by the stock Lego firmware) sent over USB from a PC to the appropriate EV3s using Christoph Gaukel's `ev3-python3` API. This rather inconvenient way of programming the Mindstorms is chosen to minimize any additional overhead caused by alternative VMs while leveraging Lego's official (very well optimized) motor drivers. Combined with a moveset optimization system that considers ~20 different corner cutting cases, each individually optimized, this pushes solving speed pretty much to Lego's absolute limits.

The most interesting parts of the code provided here are probably:

* A movement optimization system which differentiates between more than 20 different corner cutting scenarios (i.e. combinations that require different precision on the physical cube for smooth transitions) and performs individual tuning for all of them. Furthermore, it also automatically determines the optimal directions for 180 degrees turns (which can be performed both clockwise and counter-clockwise) with respect to this corner cutting.

* A robust color matching algorithm based on a transformed HSV space, clustering and confidence based assignment while taking into account all cube constraints (like for example that every edge can exist at most once). It is able to cope with the strongly varying lighting conditions on different parts of the cube (i.e. the bottom side is typically much darker than the top), distortions and amplified refelections all caused by the mirrors.

* Control of a fairly complex robot construction via highly efficient but non-trivial direct commands. This part also utilizes motor sensor measurements for more reliable move tuning (instead of being based on rather inconsistent timings).

* The source code of the highly optimized solving algorithm is located in a different repository: https://github.com/efrantar/twophase

# Further Comments

Note that the code provided here is primarily intended for people interested in the underlying techniques of an extremely fast cube-solver. In particular, as a reference / inspirations for how to effectively overcome the biggest challenges of a cube-solving robot in general as well as for pushing the Lego Mindstorms hardware to its speed limits (just please take into account that most of what you see here is quite advanced and most likely absolutely overkill if you are working on your very first cube-solver). This project is however not intended as a model to be rebuilt one-to-one and run with prewritten software, which is why no building instructions are provided (and there is no particularly user-friendly interface). There are other really cool robots designed specifically for that purpose :).

With the completion of the considerably improved 3 Mindstorm / 10 motor version and the first ever sub 1 second solve with a Lego robot, my work on mirrcub3r now finally complete. This means there will most likely not be any updates of this repository in the future. I am however far from being done with Lego cube-solvers and will probably start working on different designs very soon. So, if you are interested in my most recent color scanning, motor control, etc. code, best follow me on Github / check my other repositories.
