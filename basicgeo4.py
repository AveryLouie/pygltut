from OpenGLContext import testingcontext
BaseContext = testingcontext.getInteractive()
from OpenGL.GL import *
from OpenGL.arrays import vbo
from OpenGLContext.arrays import *
from OpenGL.GL import shaders

from OpenGLContext.events.timer import Timer

import logging
logging.basicConfig()

class TestContext(BaseContext):
	"""Demonstrates use of attribute types in GLSL"""

	def OnInit(self):
		"""initialize the context"""
		vertex = shaders.compileShader("""
			uniform float tween;
            attribute vec3 position;
            attribute vec3 tweened;
            attribute vec3 color;
            varying vec4 baseColor;
            void main() {
                gl_Position = gl_ModelViewProjectionMatrix * mix(
                    vec4( position,1.0),
                    vec4( tweened,1.0),
                    tween
				);

			baseColor = vec4(color,1.0);

			}""",GL_VERTEX_SHADER)
		
		fragment = shaders.compileShader("""
			varying vec4 baseColor;
			void main(){
			gl_FragColor = baseColor;
			}""",GL_FRAGMENT_SHADER)
		self.shader = shaders.compileProgram(vertex,fragment)

		self.vbo = vbo.VBO(
            array( [
                [  0, 1, 0, 1,3,0,  0,1,0 ],
                [ -1,-1, 0, -1,-1,0,  1,1,0 ],
                [  1,-1, 0, 1,-1,0, 0,1,1 ],
                [  2,-1, 0, 2,-1,0, 1,0,0 ],
                [  4,-1, 0, 4,-1,0, 0,1,0 ],
                [  4, 1, 0, 4,9,0, 0,0,1 ],
                [  2,-1, 0, 2,-1,0, 1,0,0 ],
                [  4, 1, 0, 1,3,0, 0,0,1 ],
                [  2, 1, 0, 1,-1,0, 0,1,1 ],
            ],'f')
        )

		self.position_location = glGetAttribLocation(
        	self.shader,'position'
        	)
		self.tweened_location = glGetAttribLocation(
        	self.shader,'tweened'
        	)
		self.color_location = glGetAttribLocation(
        	self.shader,'color'
        	)
		self.tween_location = glGetUniformLocation(
        	self.shader,'tween'
        	)

		self.time = Timer (duration = 2.0, repeating = 1)
		self.time.addEventHandler( "fraction",self.OnTimerFraction)
		self.time.register (self)
		self.time.start ()

	def Render(self,mode=0):
		"""Render geometry for the scene"""
		BaseContext.Render(self,mode)
		glUseProgram(self.shader)
		glUniform1f(self.tween_location,self.tween_fraction)
		try:
			self.vbo.bind()
			try:
				glEnableVertexAttribArray(self.position_location)
				glEnableVertexAttribArray(self.tweened_location)
				glEnableVertexAttribArray(self.color_location)
				stride = 9 * 4
				glVertexAttribPointer(
					self.position_location,
					3, GL_FLOAT, False, stride, self.vbo
					)
				glVertexAttribPointer(
					self.tweened_location,
					3, GL_FLOAT, False, stride, self.vbo+24
					)
				glDrawArrays(GL_TRIANGLES,0,9)
			finally:
				self.vbo.unbind()
				glDisableVertexAttribArray(self.position_location)
				glDisableVertexAttribArray(self.tweened_location)
				glDisableVertexAttribArray(self.color_location)
		finally:
			glUseProgram(0);

		tween_fraction = 0.0

    	def OnTimerFraction(self, event):
    		frac = event.fraction()
    		if frac>.5:
    			frac = 1.0-frac
    		frac *= 2
    		self.tween_fraction = frac
    		self.triggerRedraw()

if __name__ ==  "__main__":
	TestContext.ContextMainLoop()

