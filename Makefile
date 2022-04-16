.PHONY: doc_run

# ================================
# GIT

git_fast:
	git add -u
	git status
ifdef m
	git commit -m "$(m)"
else
	git commit -m "Fast push"
endif
ifdef b
	git push origin $(b)
else
	git push origin main
endif

git_pull:
ifdef b
	git pull origin $(b)
else
	git pull origin main
endif



# ================================
# DOCKER

connect_aws:
	ssh -i "source/secrets/misu-bot.pem" ubuntu@ec2-3-121-199-186.eu-central-1.compute.amazonaws.com

doc_build:
	-sudo docker stop misu_bot
	sudo docker build -t misu_bot .

doc_run:
ifdef k
	-sudo docker stop misu_bot
	-sudo docker rm misu_bot
	sudo docker run -e BOT_API_KEY=$(k) --name misu_bot misu_bot
else
	$(info ***** Bot Api Key is NOT provided! *****)
endif

doc_logs:
ifdef c
	sudo docker logs $(c) -f
else
	sudo docker logs misu_bot -f
endif